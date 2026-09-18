"""In-memory advisory sessions.

**Sessions live in process memory and are lost when the backend restarts.**
That is deliberate for this iteration, and documented in the README so nobody
mistakes it for durability. Persistence is a later decision.

Two design points that matter more than the storage mechanism:

**The manager's answers are held separately from anything the model produced.**
Clarification responses are written only by the endpoint the manager's own
submission reaches. No advisory output can create, alter or complete an answer.
A model that returns a comparison claiming the manager said something they did
not cannot make that true here, because the comparison never touches this field.

**Advisory outputs are append-only.** Each accepted output is added with the
turn that produced it. Nothing is overwritten, so the trace of what the advisor
concluded and when survives, and a stale result arriving late can be recognised
and dropped rather than silently replacing newer advice.

**Attempts are recorded separately from accepted outputs.** An accepted output
says what the advisor concluded; an attempt says what was actually requested and
what became of it. Keeping only the first loses the selector calls entirely,
loses the cost of a repair, and loses every request that failed, which is
exactly the set of things a person debugging a live run needs to see. Attempts
are appended as they complete, so the ones that succeeded survive a later
failure in the same turn.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.models import (
    AdvisoryAction,
    AnswerStatus,
    ClarificationBatch,
    ClarificationResponse,
    ClarificationRound,
    Comparison,
    ContextRequest,
    Diagnosis,
    ManagerBrief,
    Recommendation,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class AdvisoryRecord:
    """One accepted output, with what produced it."""

    action: AdvisoryAction
    payload: Any
    turn: int
    created_at: str
    prompt_trace: dict[str, str]
    usage: dict[str, Any] | None = None
    #: Usage of the repair call, when this output needed one. Separate from
    #: ``usage`` so the cost of a repair is visible rather than folded in.
    repair_usage: dict[str, Any] | None = None
    repaired: bool = False
    #: The answers version this output was produced against.
    answers_version: int = 0


@dataclass
class AttemptRecord:
    """One request to the provider, whatever became of it.

    ``usage_available`` is explicit rather than inferred from ``usage`` being
    empty. A failed or cancelled request has no usage to report, and inventing
    plausible token counts for it would corrupt the only record of what the run
    actually cost.
    """

    turn: int
    kind: str  # selector | action | repair
    step: str  # the action being selected or performed
    outcome: str  # accepted | rejected | failed | cancelled
    created_at: str
    prompt_trace: dict[str, str]
    usage: dict[str, Any] | None = None
    usage_available: bool = False
    detail: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "turn": self.turn,
            "kind": self.kind,
            "step": self.step,
            "outcome": self.outcome,
            "created_at": self.created_at,
            "prompt": self.prompt_trace,
            "usage": self.usage,
            "usage_available": self.usage_available,
            "usage_note": None
            if self.usage_available
            else "No usage reported by the provider for this attempt.",
            "detail": self.detail,
        }


class SessionStateError(RuntimeError):
    """An operation was attempted that the session's state does not permit."""


@dataclass
class Session:
    """One manager's advisory session."""

    id: str
    brief: ManagerBrief
    created_at: str = field(default_factory=_now)

    #: Everything the advisor produced and the application accepted.
    records: list[AdvisoryRecord] = field(default_factory=list)

    #: Every provider request attempted, in order, including selector calls,
    #: repairs, rejections, failures and cancellations. Append-only.
    attempts: list[AttemptRecord] = field(default_factory=list)

    #: Clarification rounds. The batch comes from the advisor; the responses
    #: come only from the manager, through :meth:`record_answers`.
    clarification_rounds: list[ClarificationRound] = field(default_factory=list)

    #: Indices of clarification rounds the manager has already responded to.
    #: A round the manager has had their turn on is no longer blocking, even if
    #: some questions in it were left untouched. Those become open unknowns
    #: rather than a reason to stop: a manager who answers two of three
    #: questions has still had their say, and waiting forever for the third
    #: would deadlock the session.
    responded_rounds: set[int] = field(default_factory=set)

    #: Increments once per manager-initiated turn. Used to discard stale work.
    turn: int = 0

    #: Increments whenever the manager submits answers. A comparison records the
    #: version it was made against, so the loop can tell a comparison that is
    #: still current from one the manager has since added information to.
    answers_version: int = 0

    #: Held while a turn runs, so two overlapping requests cannot both commit.
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    status: str = "ready"
    last_error: dict[str, Any] | None = None
    last_budget: dict[str, Any] | None = None

    # --- Reading -----------------------------------------------------------

    def latest(self, action: AdvisoryAction) -> Any | None:
        for record in reversed(self.records):
            if record.action is action:
                return record.payload
        return None

    def latest_record(self, action: AdvisoryAction) -> AdvisoryRecord | None:
        for record in reversed(self.records):
            if record.action is action:
                return record
        return None

    def comparison_is_current(self) -> bool:
        """Whether the stored comparison still reflects what the manager has said.

        A comparison made before the manager answered anything is out of date
        once they have. One made after is not, and re-running it would spend a
        request to produce the same analysis.
        """
        record = self.latest_record(AdvisoryAction.COMPARE)
        if record is None:
            return False
        return record.answers_version >= self.answers_version

    def clarification_rounds_opened(self) -> int:
        return len(self.clarification_rounds)

    def citable_answers(self) -> list[dict[str, str]]:
        """Answers a claim is allowed to cite, with their text.

        Only answered questions. A skipped or unanswered question produced no
        information, so nothing may rest on it. Supplied to the model as an
        explicit list, separate from the status of every question, because the
        first live run showed the model citing skipped question identifiers when
        it had only a mixed list to work from.
        """
        out: list[dict[str, str]] = []
        for round_ in self.clarification_rounds:
            questions = {q.id: q for q in round_.batch.questions}
            for response in round_.responses:
                if response.status is AnswerStatus.ANSWERED and response.answer:
                    question = questions.get(response.question_id)
                    out.append(
                        {
                            "id": response.question_id,
                            "question": question.question if question else "",
                            "answer": response.answer,
                        }
                    )
        return out

    @property
    def diagnosis(self) -> Diagnosis | None:
        return self.latest(AdvisoryAction.DIAGNOSE)

    @property
    def context_request(self) -> ContextRequest | None:
        return self.latest(AdvisoryAction.REQUEST_CONTEXT)

    @property
    def comparison(self) -> Comparison | None:
        return self.latest(AdvisoryAction.COMPARE)

    @property
    def recommendation(self) -> Recommendation | None:
        return self.latest(AdvisoryAction.RECOMMEND)

    def all_questions(self) -> list[tuple[str, str, str, AnswerStatus]]:
        """Every question asked, with its current status.

        Read from session state, never from a generated summary. A recommendation
        that forgets to mention a skipped question cannot make it disappear from
        the interface, because the interface reads this.
        """
        out: list[tuple[str, str, str, AnswerStatus]] = []
        for round_ in self.clarification_rounds:
            statuses = {r.question_id: r.status for r in round_.responses}
            for question in round_.batch.questions:
                out.append(
                    (
                        question.id,
                        question.question,
                        question.why_it_matters,
                        statuses.get(question.id, AnswerStatus.UNANSWERED),
                    )
                )
        return out

    def open_questions(self) -> list[tuple[str, str, str, AnswerStatus]]:
        return [q for q in self.all_questions() if q[3] is not AnswerStatus.ANSWERED]

    def answered_question_ids(self) -> set[str]:
        ids: set[str] = set()
        for round_ in self.clarification_rounds:
            ids |= round_.answered_ids()
        return ids

    def asked_question_ids(self) -> set[str]:
        ids: set[str] = set()
        for round_ in self.clarification_rounds:
            ids |= round_.batch.question_ids()
        return ids

    def has_pending_questions(self) -> bool:
        """True when the manager has been asked something and has not yet replied.

        Measured per round, not per question. Once the manager submits anything
        for a round, that round stops blocking: whatever they left untouched
        becomes an open unknown, visible in the interface and carried into the
        advice. Blocking on individual unanswered questions would mean a manager
        who skips one field never gets advice at all.
        """
        return any(
            index not in self.responded_rounds
            for index in range(len(self.clarification_rounds))
        )

    # --- Writing -----------------------------------------------------------

    def add_attempt(self, attempt: AttemptRecord) -> None:
        """Record one provider request. Never removed, never rewritten."""
        self.attempts.append(attempt)

    def add_record(self, record: AdvisoryRecord) -> None:
        """Append an accepted output.

        Rejects anything produced by a turn older than the current one. Without
        this, a slow request that started before the manager changed something
        could land afterwards and overwrite newer advice.
        """
        if record.turn < self.turn:
            raise SessionStateError(
                f"refusing to commit output from turn {record.turn}; "
                f"the session is on turn {self.turn}"
            )
        self.records.append(record)

    def open_clarification_round(
        self,
        batch: ClarificationBatch,
        turn: int,
        prompt_trace: dict[str, str] | None = None,
        usage: dict[str, Any] | None = None,
        repair_usage: dict[str, Any] | None = None,
        repaired: bool = False,
        answers_version: int = 0,
    ) -> None:
        """Record questions the advisor asked, all initially unanswered.

        Carries the same provenance as any other accepted output. An earlier
        version recorded clarification with an empty prompt trace and no usage,
        which made the one action a manager interacts with most the one with no
        record of what produced it.
        """
        round_ = ClarificationRound(
            batch=batch,
            responses=[
                ClarificationResponse(
                    question_id=question.id,
                    status=AnswerStatus.UNANSWERED,
                    answer=None,
                )
                for question in batch.questions
            ],
        )
        self.clarification_rounds.append(round_)
        self.add_record(
            AdvisoryRecord(
                action=AdvisoryAction.ASK_CLARIFICATION,
                payload=batch,
                turn=turn,
                created_at=_now(),
                prompt_trace=prompt_trace or {},
                usage=usage,
                repair_usage=repair_usage,
                repaired=repaired,
                answers_version=answers_version,
            )
        )

    def record_answers(self, answers: dict[str, str | None], skipped: set[str]) -> None:  # noqa: C901
        """Write the manager's own replies.

        The only path by which an answer enters the session. Advisory output
        never reaches this method, so the model cannot invent, alter or complete
        what the manager said.

        An identifier that was never asked is rejected rather than ignored.
        """
        known = self.asked_question_ids()
        unknown = sorted((set(answers) | skipped) - known)
        if unknown:
            raise SessionStateError(f"no such question in this session: {', '.join(unknown)}")

        self.answers_version += 1

        for index, round_ in enumerate(self.clarification_rounds):
            # The manager has now had their turn on this round, whatever they
            # chose to leave blank.
            self.responded_rounds.add(index)
            updated: list[ClarificationResponse] = []
            for response in round_.responses:
                qid = response.question_id

                if qid in skipped:
                    updated.append(
                        ClarificationResponse(
                            question_id=qid, status=AnswerStatus.SKIPPED, answer=None
                        )
                    )
                elif qid in answers and (answers[qid] or "").strip():
                    updated.append(
                        ClarificationResponse(
                            question_id=qid,
                            status=AnswerStatus.ANSWERED,
                            answer=answers[qid],
                        )
                    )
                else:
                    # Left exactly as it was. An answer already given is not
                    # erased by a later submission that omits it.
                    updated.append(response)

            self.clarification_rounds[index] = ClarificationRound(
                batch=round_.batch, responses=updated
            )


class SessionStore:
    """Sessions held in process memory.

    Not persistence. A restart loses everything, which is stated in the README
    and in the API's own documentation rather than left to be discovered.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self, brief: ManagerBrief) -> Session:
        session = Session(id=uuid.uuid4().hex[:12], brief=brief)
        self._sessions[session.id] = session
        return session

    def get(self, session_id: str) -> Session:
        try:
            return self._sessions[session_id]
        except KeyError as exc:
            raise SessionStateError(
                f"no session {session_id!r}. Sessions are held in memory and are lost "
                "when the backend restarts."
            ) from exc

    def exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def count(self) -> int:
        return len(self._sessions)


#: One store for the process. Replaced in tests.
store = SessionStore()
