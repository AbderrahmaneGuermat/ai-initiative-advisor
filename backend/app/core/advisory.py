"""The bounded advisory loop.

The next-action prompt decides what happens next. Python decides what is
allowed to happen, how many times, and whether the result may be kept.

Neither half is optional. Without the prompt choosing, the order would be a
script and the method's central claim would be false. Without the code
enforcing, the loop would have no ceiling and no gate on what reaches the
manager's advice.

Shape of one turn:

1. Work out which actions are permitted right now, from session state.
2. Ask the selector prompt to choose one. Rejected if it chooses otherwise.
3. Execute it, unless it is ``await_user``, which needs no model call.
4. Validate the output. On failure, one repair attempt, then stop.
5. Commit and loop, until a pause point or a limit.

Every provider request is charged to the turn budget, including the selector
and any repair.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel

from app.core import assemble
from app.core.limits import LimitExceeded, Limits, TurnBudget
from app.core.model_client import ModelClient, ModelError
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
from app.store.session import AdvisoryRecord, Session

SYSTEM_PROMPT = "system/advisor.md"
SELECTOR_PROMPT = "actions/next-action.md"
REPAIR_PROMPT = "support/repair-output.md"

#: Actions this iteration can actually carry out. ``revise`` is deliberately
#: absent: its validation exists but its user flow does not, and advertising an
#: action the application cannot complete would invite the selector to choose it
#: and then fail. Documented in the README as not yet available.
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


@dataclass
class TurnResult:
    """What one turn did, for the API layer to report."""

    session_id: str
    actions: list[str] = field(default_factory=list)
    stopped_because: str = "completed"
    awaiting_user: bool = False
    error: dict[str, Any] | None = None
    budget: dict[str, Any] = field(default_factory=dict)
    traces: list[dict[str, Any]] = field(default_factory=list)


def permitted_actions(session: Session) -> set[AdvisoryAction]:
    """What the advisor may choose right now, from session state alone.

    Prerequisites live here rather than in a prompt, because a prompt that could
    waive its own prerequisites is not enforcing them.
    """
    brief = session.brief
    allowed: set[AdvisoryAction] = {AdvisoryAction.AWAIT_USER}

    # Nothing to work with at all.
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

    async def run_turn(self, session: Session) -> TurnResult:
        """Advance the session until it pauses or hits a limit.

        The session lock is held throughout, so two overlapping requests cannot
        both commit. The second waits, then runs against the state the first
        left behind rather than the state it started from.
        """
        async with session.lock:
            session.turn += 1
            turn = session.turn
            result = TurnResult(session_id=session.id)
            budget = TurnBudget(limits=self._limits)
            started = time.monotonic()
            session.status = "running"

            try:
                while True:
                    budget.check_time(time.monotonic() - started)

                    permitted = permitted_actions(session)
                    if not permitted:
                        result.stopped_because = "no action is available"
                        break

                    action = await self._select_action(session, permitted, budget, result)

                    if action is AdvisoryAction.AWAIT_USER:
                        # No model call. Nothing to generate, and a request here
                        # would be spent producing a sentence nobody needs.
                        result.actions.append(action.value)
                        result.awaiting_user = True
                        result.stopped_because = "waiting for the manager"
                        break

                    budget.charge_action()
                    await self._execute(session, action, turn, budget, result)
                    result.actions.append(action.value)

                    if action in (
                        AdvisoryAction.ASK_CLARIFICATION,
                        AdvisoryAction.REQUEST_CONTEXT,
                    ):
                        result.awaiting_user = True
                        result.stopped_because = "waiting for the manager"
                        break

                    if action is AdvisoryAction.RECOMMEND:
                        result.stopped_because = "recommendation ready"
                        break

                session.status = "ready"

            except LimitExceeded as exc:
                session.status = "ready"
                result.stopped_because = f"limit reached: {exc.limit_name}"
                result.error = {
                    "kind": "limit",
                    "limit": exc.limit_name,
                    "message": exc.detail,
                    "recoverable": True,
                }
            except OutputRejected as exc:
                session.status = "ready"
                result.stopped_because = "output rejected"
                result.error = {
                    "kind": "invalid_output",
                    "message": "The advisor's answer did not pass validation and was discarded.",
                    "details": exc.errors,
                    "recoverable": True,
                }
            except ModelError as exc:
                session.status = "ready"
                result.stopped_because = "model error"
                result.error = {
                    "kind": type(exc).__name__,
                    "message": exc.user_message,
                    "recoverable": exc.recoverable,
                }
            except PromptError as exc:
                session.status = "ready"
                result.stopped_because = "prompt error"
                result.error = {
                    "kind": "prompt",
                    "message": "A runtime prompt file is missing or malformed.",
                    "details": [str(exc)],
                    "recoverable": False,
                }

            budget.elapsed_seconds = time.monotonic() - started
            result.budget = budget.summary()
            session.last_budget = result.budget
            session.last_error = result.error
            return result

    # --- Selection --------------------------------------------------------

    async def _select_action(
        self,
        session: Session,
        permitted: set[AdvisoryAction],
        budget: TurnBudget,
        result: TurnResult,
    ) -> AdvisoryAction:
        system = load_prompt(SYSTEM_PROMPT)
        selector = load_prompt(SELECTOR_PROMPT)

        instructions = f"{system.body}\n\n---\n\n{selector.body}"
        input_text = assemble.selector_input(session, permitted)
        budget.check_input_size(input_text)

        budget.charge_model_request()
        call = await self._client.complete(
            instructions=instructions,
            input_text=input_text,
            schema=wire_models.WireNextAction,
            schema_name="WireNextAction",
        )

        result.traces.append(
            {
                "step": "select",
                **selector.trace(),
                "system_hash": system.short_hash,
                "usage": call.usage(),
            }
        )

        decision = validate_next_action(call.parsed, permitted)
        return decision.action

    # --- Execution --------------------------------------------------------

    async def _execute(
        self,
        session: Session,
        action: AdvisoryAction,
        turn: int,
        budget: TurnBudget,
        result: TurnResult,
    ) -> None:
        system = load_prompt(SYSTEM_PROMPT)
        action_prompt = load_prompt(ACTION_PROMPTS[action])
        schema = WIRE_SCHEMAS[action]

        instructions = f"{system.body}\n\n---\n\n{action_prompt.body}"
        input_text = assemble.action_input(session, action)
        budget.check_input_size(input_text)

        budget.charge_model_request()
        call = await self._client.complete(
            instructions=instructions,
            input_text=input_text,
            schema=schema,
            schema_name=schema.__name__,
        )

        trace = {"step": action.value, **action_prompt.trace(), "usage": call.usage()}

        context = validation_context(session)

        try:
            payload = validate_output(action, call.parsed, context)
            trace["repaired"] = False
        except OutputRejected as rejection:
            # Exactly one repair attempt. It is charged to the same budget as
            # everything else, so a repair cannot buy extra requests, and a
            # failed repair is not retried in a different form.
            payload, repair_call = await self._repair(
                session=session,
                action=action,
                schema=schema,
                rejected=call.parsed,
                rejection=rejection,
                context=context,
                budget=budget,
            )
            trace["repaired"] = True
            trace["repair_usage"] = repair_call.usage()
            trace["original_errors"] = rejection.errors

        result.traces.append(trace)
        self._commit(session, action, payload, turn, action_prompt.trace(), call.usage())

    async def _repair(
        self,
        *,
        session: Session,
        action: AdvisoryAction,
        schema: type[BaseModel],
        rejected: BaseModel,
        rejection: OutputRejected,
        context: ValidationContext,
        budget: TurnBudget,
    ) -> tuple[Any, Any]:
        system = load_prompt(SYSTEM_PROMPT)
        action_prompt = load_prompt(ACTION_PROMPTS[action])
        repair_prompt = load_prompt(REPAIR_PROMPT)

        instructions = (
            f"{system.body}\n\n---\n\n{action_prompt.body}\n\n---\n\n{repair_prompt.body}"
        )
        input_text = assemble.repair_input(
            session=session,
            action=action,
            rejected=rejected,
            errors=rejection.errors,
        )
        budget.check_input_size(input_text)

        budget.charge_model_request()
        call = await self._client.complete(
            instructions=instructions,
            input_text=input_text,
            schema=schema,
            schema_name=schema.__name__,
        )

        # A failed repair raises, and this is the end of it. There is no second
        # repair, and no fallback that writes something weaker to the session.
        payload = validate_output(action, call.parsed, context)
        return payload, call

    # --- Commit -----------------------------------------------------------

    @staticmethod
    def _commit(
        session: Session,
        action: AdvisoryAction,
        payload: Any,
        turn: int,
        prompt_trace: dict[str, str],
        usage: dict[str, Any],
    ) -> None:
        if isinstance(payload, ClarificationBatch):
            # Goes through the session's own method, which creates one
            # unanswered response per question. Answers arrive only from the
            # manager, through a different path entirely.
            session.open_clarification_round(payload, turn)
            return

        if not isinstance(payload, (Diagnosis, Comparison, Recommendation, AwaitUser)) and not (
            action is AdvisoryAction.REQUEST_CONTEXT
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
            )
        )


def _timestamp() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def dump_for_prompt(payload: BaseModel) -> str:
    """Render a contract instance for inclusion in a prompt."""
    return json.dumps(payload.model_dump(mode="json"), indent=2, ensure_ascii=False)
