"""The permitted advisory actions and what each one must produce.

This module is the action contract described in docs/architecture.md, section 2.
A prompt chooses what to do next; this file fixes what it is allowed to choose
from and what the result has to look like. The choice is judgement and belongs
in a prompt. The set of permissible choices is a boundary and belongs here,
where a prompt cannot widen it.

``diagnose`` is a permitted action. An earlier revision described a diagnosis
prompt without a matching action, which made that prompt unreachable. The fix
was to bind actions and output contracts together in one declaration, so the two
cannot drift apart again. See docs/decisions.md, D-017.
"""

from __future__ import annotations

from enum import Enum

from pydantic import Field

from app.models.clarification import ClarificationBatch
from app.models.common import Claim, NonEmptyText, SourceRef, StrictModel
from app.models.comparison import Comparison
from app.models.recommendation import Recommendation, Revision


class AdvisoryAction(str, Enum):
    """Everything the advisor may decide to do next.

    A value outside this set fails validation. That is the point: an
    unrecognised action is rejected rather than improvised around.
    """

    DIAGNOSE = "diagnose"
    REQUEST_CONTEXT = "request_context"
    ASK_CLARIFICATION = "ask_clarification"
    COMPARE = "compare"
    RECOMMEND = "recommend"
    REVISE = "revise"
    AWAIT_USER = "await_user"


class NextAction(StrictModel):
    """What the advisor has decided to do, and why.

    The reasoning is required. It is not used for control flow, and no code
    inspects it. It exists so a reviewer reading a transcript can see why the
    advisor went where it went, which is the part of an adaptive loop that is
    otherwise invisible.
    """

    action: AdvisoryAction
    reasoning: NonEmptyText


# --- Outputs for actions that have no contract elsewhere ------------------


class Gap(StrictModel):
    """Something absent, contradictory or assumed, found while reading the brief."""

    description: NonEmptyText
    # Why it matters for the advice. Required: an observation that changes
    # nothing is noise in a diagnosis.
    why_it_matters: NonEmptyText
    relates_to: list[SourceRef] = []


class Diagnosis(StrictModel):
    """The advisor's reading of the brief before it acts on it."""

    context_id: NonEmptyText
    gaps: list[Gap] = Field(default=[], description="What the brief does not say but needs to")
    contradictions: list[Gap] = Field(default=[], description="Where the brief conflicts with itself")
    unstated_assumptions: list[Gap] = Field(
        default=[],
        description="What the brief takes for granted without saying so",
    )
    summary: NonEmptyText


class MissingInput(StrictModel):
    """An essential input the advisor cannot proceed without."""

    field: NonEmptyText = Field(description="What is needed, in the manager's terms")
    why_required: NonEmptyText


class ContextRequest(StrictModel):
    """Issued when essential inputs are absent entirely.

    Distinct from clarification. Clarification refines a brief that exists;
    this says there is not enough to work with yet.
    """

    missing: list[MissingInput] = Field(min_length=1)
    message: NonEmptyText


class AwaitUser(StrictModel):
    """Nothing useful can happen until the manager responds.

    The one action with no prompt behind it. It ends the turn and hands control
    back. A contract is declared anyway so the action-to-output mapping is total
    and no action is a special case.
    """

    reason: NonEmptyText
    awaiting: list[Claim] = Field(
        default=[],
        description="What specifically is being waited on",
    )


#: The single declaration binding each action to the contract its output must
#: satisfy. Documented in docs/architecture.md, section 2, and checked by a test
#: that fails if an action is added without a contract.
ACTION_OUTPUT_CONTRACTS: dict[AdvisoryAction, type[StrictModel]] = {
    AdvisoryAction.DIAGNOSE: Diagnosis,
    AdvisoryAction.REQUEST_CONTEXT: ContextRequest,
    AdvisoryAction.ASK_CLARIFICATION: ClarificationBatch,
    AdvisoryAction.COMPARE: Comparison,
    AdvisoryAction.RECOMMEND: Recommendation,
    AdvisoryAction.REVISE: Revision,
    AdvisoryAction.AWAIT_USER: AwaitUser,
}

#: Actions performed by a runtime prompt. ``await_user`` is excluded because it
#: produces no model output. The prompt files themselves are not written yet.
ACTION_PROMPTS: dict[AdvisoryAction, str] = {
    AdvisoryAction.DIAGNOSE: "actions/diagnose.md",
    AdvisoryAction.REQUEST_CONTEXT: "actions/request-context.md",
    AdvisoryAction.ASK_CLARIFICATION: "actions/clarify.md",
    AdvisoryAction.COMPARE: "actions/compare.md",
    AdvisoryAction.RECOMMEND: "actions/recommend.md",
    AdvisoryAction.REVISE: "actions/revise.md",
}


def output_contract_for(action: AdvisoryAction) -> type[StrictModel]:
    """The contract an action's output must satisfy.

    Raises rather than returning a permissive default, because a default here
    would let an unmapped action through unvalidated.
    """
    try:
        return ACTION_OUTPUT_CONTRACTS[action]
    except KeyError as exc:  # pragma: no cover - unreachable while the test holds
        raise ValueError(f"no output contract declared for action {action!r}") from exc
