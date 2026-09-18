"""The bounded advisory loop.

The next-action prompt decides what happens next. Python decides what is
allowed to happen, how many times, how long it may take, and whether the result
may be kept.

Neither half is optional. Without the prompt choosing, the order would be a
script and the method's central claim would be false. Without the code
enforcing, the loop would have no ceiling and no gate on what reaches the
manager's advice.

Shape of one turn:

1. Take the session lock. Any mutation the caller needs to make first, such as
   recording the manager's answers, happens here, inside the lock, so a turn
   cannot run against answers that change underneath it.
2. Work out which actions are permitted right now, from session state.
3. Ask the selector prompt to choose one. Rejected if it chooses otherwise.
4. Execute it, unless it is ``await_user``, which needs no model call.
5. Validate the output. On failure, one repair attempt, then stop.
6. Commit and loop, until a pause point or a limit.

Every provider request is charged to the turn budget, bounded by the remaining
wall-clock deadline, and recorded as an attempt whatever becomes of it.
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

from pydantic import BaseModel

from app.core import assemble
from app.core.limits import LimitExceeded, Limits, TurnBudget
from app.core.model_client import ModelCall, ModelClient, ModelError
from app.core.prompt_loader import PromptError, load_prompt
from app.core.validation import (
    OutputRejected,
    ValidationContext,
    validate_next_action,
    validate_output,
)
from app.models import (
    ACTION_PROMPTS,
    AdvisoryAction,
    AwaitUser,
    ClarificationBatch,
    Comparison,
    Diagnosis,
    Recommendation,
)
from app.models import wire as wire_models
from app.store.session import AdvisoryRecord, AttemptRecord, Session

SYSTEM_PROMPT = "system/advisor.md"
SELECTOR_PROMPT = "actions/next-action.md"
REPAIR_PROMPT = "support/repair-output.md"

#: Actions this iteration can actually carry out. ``revise`` is deliberately
#: absent: its validation exists but its user flow does not, and advertising an
#: action the application cannot complete would invite the selector to choose it
#: and then fail.
SUPPORTED_ACTIONS: set[AdvisoryAction] = {
    AdvisoryAction.DIAGNOSE,
    AdvisoryAction.REQUEST_CONTEXT,
    AdvisoryAction.ASK_CLARIFICATION,
    AdvisoryAction.COMPARE,
    AdvisoryAction.RECOMMEND,
    AdvisoryAction.AWAIT_USER,
}

#: Wire schema for each action's output.
WIRE_SCHEMAS: dict[AdvisoryAction, type[BaseModel]] = {
    AdvisoryAction.DIAGNOSE: wire_models.WireDiagnosis,
    AdvisoryAction.REQUEST_CONTEXT: wire_models.WireContextRequest,
    AdvisoryAction.ASK_CLARIFICATION: wire_models.WireClarificationBatch,
    AdvisoryAction.COMPARE: wire_models.WireComparison,
    AdvisoryAction.RECOMMEND: wire_models.WireRecommendation,
}


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class TurnResult:
    """What one turn did, for the API layer to report."""

    session_id: str
    actions: list[str] = field(default_factory=list)
    stopped_because: str = "completed"
    awaiting_user: bool = False
    error: dict[str, Any] | None = None
    budget: dict[str, Any] = field(default_factory=dict)
    attempts: list[dict[str, Any]] = field(default_factory=list)


def permitted_actions(session: Session) -> set[AdvisoryAction]:
    """What the advisor may choose right now, from session state alone.

    Prerequisites live here rather than in a prompt, because a prompt that could
    waive its own prerequisites is not enforcing them.
    """
    brief = session.brief
    allowed: set[AdvisoryAction] = {AdvisoryAction.AWAIT_USER}

    if not brief.initiatives or not brief.objectives:
        allowed.add(AdvisoryAction.REQUEST_CONTEXT)
        if session.diagnosis is None:
            allowed.add(AdvisoryAction.DIAGNOSE)
        return allowed & SUPPORTED_ACTIONS

    if session.diagnosis is None:
        allowed.add(AdvisoryAction.DIAGNOSE)

    # Do not ask again while the manager has questions in front of them.
    if not session.has_pending_questions():
        allowed.add(AdvisoryAction.ASK_CLARIFICATION)
        allowed.add(AdvisoryAction.COMPARE)

        if session.comparison is not None:
            allowed.add(AdvisoryAction.RECOMMEND)

    return allowed & SUPPORTED_ACTIONS


def validation_context(session: Session) -> ValidationContext:
    return ValidationContext(
        brief=session.brief,
        clarification_rounds=list(session.clarification_rounds),
        comparison=session.comparison,
    )


class AdvisoryEngine:
    """Runs advisory turns for a session."""

    def __init__(self, client: ModelClient, limits: Limits | None = None) -> None:
        self._client = client
        self._limits = limits or Limits()

    async def run_turn(
        self,
        session: Session,
        prepare: Callable[[], None] | None = None,
    ) -> TurnResult:
        """Advance the session until it pauses or hits a limit.

        ``prepare`` runs once, inside the session lock, before anything else. It
        is how the manager's answers are written: doing it outside the lock
        would let answers change while a turn was mid-flight, so the advice
        could be generated against one set of answers and committed against
        another.

        A failure in ``prepare`` propagates to the caller with nothing else
        attempted. The lock is released either way.

        The lock is the only one in the system. Nothing inside it acquires
        another, so there is no ordering to get wrong and no deadlock to have.
        """
        async with session.lock:
            if prepare is not None:
                # Deliberately outside the try below: a bad submission is the
                # caller's error to handle, not a turn that failed.
                prepare()

            session.turn += 1
            turn = session.turn
            result = TurnResult(session_id=session.id)
            budget = TurnBudget(limits=self._limits)
            budget.start()
            session.status = "running"

            try:
                await self._loop(session, turn, budget, result)
            except LimitExceeded as exc:
                result.stopped_because = f"limit reached: {exc.limit_name}"
                result.error = {
                    "kind": "limit",
                    "limit": exc.limit_name,
                    "message": self._limit_message(exc),
                    "recoverable": True,
                }
            except OutputRejected as exc:
                result.stopped_because = "output rejected"
                result.error = {
                    "kind": "invalid_output",
                    "message": "The advisor's answer did not pass validation and was discarded.",
                    "details": exc.errors,
                    "recoverable": True,
                }
            except ModelError as exc:
                result.stopped_because = "model error"
                result.error = {
                    "kind": type(exc).__name__,
                    "message": exc.user_message,
                    "recoverable": exc.recoverable,
                }
            except PromptError as exc:
                result.stopped_because = "prompt error"
                result.error = {
                    "kind": "prompt",
                    "message": "A runtime prompt file is missing or malformed.",
                    "details": [str(exc)],
                    "recoverable": False,
                }
            finally:
                # Whatever happened, including a deadline overrun or a
                # cancellation, the session must be left usable and the lock
                # released. `async with` handles the lock; this handles status.
                session.status = "ready"
                result.budget = budget.summary()
                result.attempts = [
                    attempt.as_dict() for attempt in session.attempts if attempt.turn == turn
                ]
                session.last_budget = result.budget
                session.last_error = result.error

            return result

    @staticmethod
    def _limit_message(exc: LimitExceeded) -> str:
        if exc.limit_name == "max_turn_seconds":
            return (
                "The advisor ran out of time and was stopped. Nothing partial was saved. "
                "You can try again."
            )
        return "The advisor reached a limit for this step and stopped."

    async def _loop(
        self,
        session: Session,
        turn: int,
        budget: TurnBudget,
        result: TurnResult,
    ) -> None:
        while True:
            budget.require_time("the advisory loop")

            permitted = permitted_actions(session)
            if not permitted:
                result.stopped_because = "no action is available"
                return

            action = await self._select_action(session, turn, permitted, budget)

            if action is AdvisoryAction.AWAIT_USER:
                # No model call. Nothing to generate, and a request here would
                # be spent producing a sentence nobody needs.
                result.actions.append(action.value)
                result.awaiting_user = True
                result.stopped_because = "waiting for the manager"
                return

            budget.charge_action()
            await self._execute(session, action, turn, budget)
            result.actions.append(action.value)

            if action in (AdvisoryAction.ASK_CLARIFICATION, AdvisoryAction.REQUEST_CONTEXT):
                result.awaiting_user = True
                result.stopped_because = "waiting for the manager"
                return

            if action is AdvisoryAction.RECOMMEND:
                result.stopped_because = "recommendation ready"
                return

    # --- One provider request ---------------------------------------------

    async def _request(
        self,
        *,
        session: Session,
        turn: int,
        budget: TurnBudget,
        kind: str,
        step: str,
        prompt_trace: dict[str, str],
        instructions: str,
        input_text: str,
        schema: type[BaseModel],
    ) -> ModelCall:
        """Make one call, bounded by the deadline, recorded whatever happens.

        The deadline is applied twice on purpose: as a timeout around the await,
        so an overdue call is cancelled rather than left running, and again
        afterwards, so a result that arrives past the deadline is not committed.
        """
        budget.check_input_size(input_text)

        # Time first, then charge. Charging before the deadline check would
        # count a request that was never sent.
        remaining = budget.require_time(step)
        budget.charge_model_request()

        try:
            call = await asyncio.wait_for(
                self._client.complete(
                    instructions=instructions,
                    input_text=input_text,
                    schema=schema,
                    schema_name=schema.__name__,
                ),
                timeout=remaining,
            )
        except (asyncio.TimeoutError, TimeoutError) as exc:
            session.add_attempt(
                AttemptRecord(
                    turn=turn,
                    kind=kind,
                    step=step,
                    outcome="cancelled",
                    created_at=_timestamp(),
                    prompt_trace=prompt_trace,
                    usage=None,
                    usage_available=False,
                    detail=["cancelled by the turn deadline before the provider responded"],
                )
            )
            raise budget.expired(step) from exc
        except ModelError as exc:
            session.add_attempt(
                AttemptRecord(
                    turn=turn,
                    kind=kind,
                    step=step,
                    outcome="failed",
                    created_at=_timestamp(),
                    prompt_trace=prompt_trace,
                    usage=None,
                    usage_available=False,
                    detail=[f"{type(exc).__name__}: {exc.detail or exc.user_message}"],
                )
            )
            raise

        # The call finished. If it finished late, its result is not usable: the
        # deadline exists to bound the turn, not merely to notice afterwards.
        try:
            budget.require_time(step)
        except LimitExceeded:
            session.add_attempt(
                AttemptRecord(
                    turn=turn,
                    kind=kind,
                    step=step,
                    outcome="cancelled",
                    created_at=_timestamp(),
                    prompt_trace=prompt_trace,
                    usage=call.usage(),
                    usage_available=True,
                    detail=["completed after the turn deadline; result discarded, not committed"],
                )
            )
            raise

        return call

    # --- Selection --------------------------------------------------------

    async def _select_action(
        self,
        session: Session,
        turn: int,
        permitted: set[AdvisoryAction],
        budget: TurnBudget,
    ) -> AdvisoryAction:
        system = load_prompt(SYSTEM_PROMPT)
        selector = load_prompt(SELECTOR_PROMPT)

        trace = {**selector.trace(), "system_hash": system.short_hash}

        call = await self._request(
            session=session,
            turn=turn,
            budget=budget,
            kind="selector",
            step="select",
            prompt_trace=trace,
            instructions=f"{system.body}\n\n---\n\n{selector.body}",
            input_text=assemble.selector_input(session, permitted),
            schema=wire_models.WireNextAction,
        )

        try:
            decision = validate_next_action(call.parsed, permitted)
        except OutputRejected as rejection:
            session.add_attempt(
                AttemptRecord(
                    turn=turn,
                    kind="selector",
                    step="select",
                    outcome="rejected",
                    created_at=_timestamp(),
                    prompt_trace=trace,
                    usage=call.usage(),
                    usage_available=True,
                    detail=rejection.errors,
                )
            )
            raise

        session.add_attempt(
            AttemptRecord(
                turn=turn,
                kind="selector",
                step="select",
                outcome="accepted",
                created_at=_timestamp(),
                prompt_trace=trace,
                usage=call.usage(),
                usage_available=True,
                detail=[f"chose {decision.action.value}"],
            )
        )
        return decision.action

    # --- Execution --------------------------------------------------------

    async def _execute(
        self,
        session: Session,
        action: AdvisoryAction,
        turn: int,
        budget: TurnBudget,
    ) -> None:
        system = load_prompt(SYSTEM_PROMPT)
        action_prompt = load_prompt(ACTION_PROMPTS[action])
        schema = WIRE_SCHEMAS[action]
        trace = {**action_prompt.trace(), "system_hash": system.short_hash}

        call = await self._request(
            session=session,
            turn=turn,
            budget=budget,
            kind="action",
            step=action.value,
            prompt_trace=trace,
            instructions=f"{system.body}\n\n---\n\n{action_prompt.body}",
            input_text=assemble.action_input(session, action),
            schema=schema,
        )

        context = validation_context(session)
        repair_usage: dict[str, Any] | None = None
        repaired = False

        try:
            payload = validate_output(action, call.parsed, context)
            session.add_attempt(
                AttemptRecord(
                    turn=turn,
                    kind="action",
                    step=action.value,
                    outcome="accepted",
                    created_at=_timestamp(),
                    prompt_trace=trace,
                    usage=call.usage(),
                    usage_available=True,
                )
            )
        except OutputRejected as rejection:
            session.add_attempt(
                AttemptRecord(
                    turn=turn,
                    kind="action",
                    step=action.value,
                    outcome="rejected",
                    created_at=_timestamp(),
                    prompt_trace=trace,
                    usage=call.usage(),
                    usage_available=True,
                    detail=rejection.errors,
                )
            )
            # Exactly one repair attempt, charged to the same budget and bounded
            # by the same deadline. A failed repair is not retried in another
            # form, and nothing weaker is written in its place.
            payload, repair_call = await self._repair(
                session=session,
                turn=turn,
                action=action,
                schema=schema,
                rejected=call.parsed,
                rejection=rejection,
                context=context,
                budget=budget,
            )
            repair_usage = repair_call.usage()
            repaired = True

        self._commit(
            session=session,
            action=action,
            payload=payload,
            turn=turn,
            prompt_trace=trace,
            usage=call.usage(),
            repair_usage=repair_usage,
            repaired=repaired,
        )

    async def _repair(
        self,
        *,
        session: Session,
        turn: int,
        action: AdvisoryAction,
        schema: type[BaseModel],
        rejected: BaseModel,
        rejection: OutputRejected,
        context: ValidationContext,
        budget: TurnBudget,
    ) -> tuple[Any, ModelCall]:
        system = load_prompt(SYSTEM_PROMPT)
        action_prompt = load_prompt(ACTION_PROMPTS[action])
        repair_prompt = load_prompt(REPAIR_PROMPT)
        trace = {
            **repair_prompt.trace(),
            "system_hash": system.short_hash,
            "repairing": action_prompt.id,
        }

        call = await self._request(
            session=session,
            turn=turn,
            budget=budget,
            kind="repair",
            step=action.value,
            prompt_trace=trace,
            instructions=(
                f"{system.body}\n\n---\n\n{action_prompt.body}\n\n---\n\n{repair_prompt.body}"
            ),
            input_text=assemble.repair_input(
                session=session,
                action=action,
                rejected=rejected,
                errors=rejection.errors,
            ),
            schema=schema,
        )

        try:
            payload = validate_output(action, call.parsed, context)
        except OutputRejected as second:
            session.add_attempt(
                AttemptRecord(
                    turn=turn,
                    kind="repair",
                    step=action.value,
                    outcome="rejected",
                    created_at=_timestamp(),
                    prompt_trace=trace,
                    usage=call.usage(),
                    usage_available=True,
                    detail=second.errors,
                )
            )
            raise

        session.add_attempt(
            AttemptRecord(
                turn=turn,
                kind="repair",
                step=action.value,
                outcome="accepted",
                created_at=_timestamp(),
                prompt_trace=trace,
                usage=call.usage(),
                usage_available=True,
            )
        )
        return payload, call

    # --- Commit -----------------------------------------------------------

    @staticmethod
    def _commit(
        *,
        session: Session,
        action: AdvisoryAction,
        payload: Any,
        turn: int,
        prompt_trace: dict[str, str],
        usage: dict[str, Any],
        repair_usage: dict[str, Any] | None,
        repaired: bool,
    ) -> None:
        if isinstance(payload, ClarificationBatch):
            # Goes through the session's own method, which creates one
            # unanswered response per question. Answers arrive only from the
            # manager, through a different path entirely.
            session.open_clarification_round(
                payload,
                turn,
                prompt_trace=prompt_trace,
                usage=usage,
                repair_usage=repair_usage,
                repaired=repaired,
            )
            return

        if not isinstance(payload, (Diagnosis, Comparison, Recommendation, AwaitUser)) and (
            action is not AdvisoryAction.REQUEST_CONTEXT
        ):
            raise OutputRejected([f"unexpected payload type for {action.value}"])

        session.add_record(
            AdvisoryRecord(
                action=action,
                payload=payload,
                turn=turn,
                created_at=_timestamp(),
                prompt_trace=prompt_trace,
                usage=usage,
                repair_usage=repair_usage,
                repaired=repaired,
            )
        )


def dump_for_prompt(payload: BaseModel) -> str:
    """Render a contract instance for inclusion in a prompt."""
    return json.dumps(payload.model_dump(mode="json"), indent=2, ensure_ascii=False)


__all__ = [
    "SUPPORTED_ACTIONS",
    "WIRE_SCHEMAS",
    "AdvisoryEngine",
    "TurnResult",
    "dump_for_prompt",
    "permitted_actions",
    "validation_context",
    "time",
]
