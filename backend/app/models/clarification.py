"""Clarification questions and what came back, including what did not.

The central requirement is that a question the manager declined to answer stays
visible. Three states are modelled explicitly rather than inferred from a
missing value:

- ``answered``   the manager replied
- ``skipped``    the manager was asked and chose not to reply
- ``unanswered`` the manager has not yet engaged with the question

Collapsing ``skipped`` and ``unanswered`` into "no answer" would lose the
distinction that matters. A skipped question is a decision the manager made, and
the advisor has to carry it forward as an open unknown or an explicit
assumption rather than quietly proceeding as if it had been answered.
"""

from __future__ import annotations

from enum import Enum

from pydantic import Field, model_validator

from app.models.common import NonEmptyText, QuestionId, SourceRef, StrictModel

#: Ceiling on questions per batch, from docs/requirements.md, C6. A limit on
#: how much is asked at once, not on how many rounds may happen.
MAX_QUESTIONS_PER_BATCH = 3


class ClarificationQuestion(StrictModel):
    """One question the advisor wants answered before it proceeds."""

    id: QuestionId
    question: NonEmptyText
    # Why this question is decision-critical. Required, because a question that
    # cannot be justified should not be asked. The contract forces the producer
    # to write the justification down; it cannot check that the justification is
    # sound.
    why_it_matters: NonEmptyText
    # What in the brief prompted the question. May be empty when the question is
    # about something the brief never mentioned.
    relates_to: list[SourceRef] = []


class ClarificationBatch(StrictModel):
    """A set of questions put to the manager at once.

    At most three, per the requirement. The limit is enforced here rather than
    requested in prompt text, because a limit that a prompt can talk itself out
    of is not a limit.
    """

    questions: list[ClarificationQuestion] = Field(min_length=1, max_length=MAX_QUESTIONS_PER_BATCH)

    @model_validator(mode="after")
    def _question_ids_are_unique(self) -> ClarificationBatch:
        ids = [q.id for q in self.questions]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate question identifiers: {', '.join(duplicates)}")
        return self

    def question_ids(self) -> set[str]:
        return {q.id for q in self.questions}


class AnswerStatus(str, Enum):
    ANSWERED = "answered"
    SKIPPED = "skipped"
    UNANSWERED = "unanswered"


class ClarificationResponse(StrictModel):
    """What came back for one question.

    ``answer`` and ``status`` are kept consistent by a validator, so the two
    cannot disagree. An answered question must carry text; a skipped or
    unanswered one must not, because text attached to a skip would be the
    advisor's inference dressed as the manager's words.
    """

    question_id: QuestionId
    status: AnswerStatus
    answer: str | None = Field(
        description="The manager's words when answered; null when skipped or unanswered",
    )

    @model_validator(mode="after")
    def _status_and_answer_agree(self) -> ClarificationResponse:
        if self.status is AnswerStatus.ANSWERED:
            if self.answer is None or not self.answer.strip():
                raise ValueError("an answered question must carry a non-empty answer")
        elif self.answer is not None:
            raise ValueError(
                f"a {self.status.value} question must have answer=null, "
                "so that nothing is attributed to a manager who did not reply"
            )
        return self

    @property
    def is_open(self) -> bool:
        """True when this question is still an open unknown.

        Both skipped and unanswered questions are open. They differ in how they
        got there, which is why the status is kept, but neither yields
        information the advice may rely on.
        """
        return self.status is not AnswerStatus.ANSWERED


class ClarificationRound(StrictModel):
    """A batch together with its responses.

    Every question gets a response entry, including the ones nobody touched.
    That is what keeps an unanswered question visible instead of absent: absence
    is indistinguishable from never having been asked.
    """

    batch: ClarificationBatch
    responses: list[ClarificationResponse] = []

    @model_validator(mode="after")
    def _responses_match_the_batch(self) -> ClarificationRound:
        asked = self.batch.question_ids()
        answered_ids = [r.question_id for r in self.responses]

        duplicates = sorted({i for i in answered_ids if answered_ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"duplicate responses for: {', '.join(duplicates)}")

        unknown = sorted(set(answered_ids) - asked)
        if unknown:
            raise ValueError(f"responses reference questions not in the batch: {', '.join(unknown)}")

        missing = sorted(asked - set(answered_ids))
        if missing:
            raise ValueError(
                "every question must have a response entry, including unanswered ones; "
                f"missing: {', '.join(missing)}"
            )
        return self

    def answered_ids(self) -> set[str]:
        """Identifiers usable as a source reference.

        Only answered questions qualify. A skipped question produced no input,
        so a claim cannot cite it.
        """
        return {r.question_id for r in self.responses if r.status is AnswerStatus.ANSWERED}

    def open_questions(self) -> list[ClarificationResponse]:
        """Everything still unknown, skipped or simply untouched."""
        return [r for r in self.responses if r.is_open]
