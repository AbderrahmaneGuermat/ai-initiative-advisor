"""The one boundary every advisory output crosses before it reaches state.

Nothing the model produces is written to a session without passing through
:func:`validate_output`. There is a single entry point on purpose: a second
path is a hole, and a hole in this particular wall means unchecked model output
becoming the manager's advice.

What is checked, in order:

1. **The output contract.** The wire object is promoted to the strict
   application contract, where identifier patterns, length minimums, the
   three-question cap and the cross-field rules all apply. The API cannot
   enforce any of these, so this is where they happen.
2. **Context identity.** The output must name the session's own context. An
   output carrying an unrelated identifier is rejected rather than attached to
   whatever session happened to receive it.
3. **References.** Every cited objective, constraint, initiative and answered
   question must exist. Every initiative named directly must be one the manager
   listed.
4. **Question identity and answer status.** New questions must not collide with
   questions already asked, and nothing may cite a question the manager skipped
   or has not answered.
5. **Required prior outputs.** A recommendation without a comparison behind it
   is rejected, as is one that does not account for every compared initiative.
6. **Revision snapshots.** A revision must name two real snapshots, and every
   constraint change it reports must match what those snapshots actually say.

What this does **not** establish is unchanged from D-016: that a claim is true,
that a citation supports the claim citing it, or that the analysis is sound.
Every check here is structural.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ValidationError

from app.models import (
    AdvisoryAction,
    AnswerStatus,
    ClarificationBatch,
    ClarificationRound,
    Comparison,
    ContextRequest,
    Diagnosis,
    ManagerBrief,
    NextAction,
    Recommendation,
    ReferenceIndex,
    Revision,
    SourceKind,
    collect_source_refs,
    output_contract_for,
)


class OutputRejected(ValueError):
    """An output failed validation and must not reach session state.

    ``errors`` is written for the repair prompt: each entry names one concrete
    problem, in terms the model can act on.
    """

    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors) if errors else "output rejected")
        self.errors = errors


@dataclass
class ValidationContext:
    """Everything needed to judge an output, assembled from the session.

    Passed explicitly rather than read from a store, so the boundary can be
    tested without a session and cannot be bypassed by whoever calls it.
    """

    brief: ManagerBrief
    clarification_rounds: list[ClarificationRound] = field(default_factory=list)
    comparison: Comparison | None = None

    #: For revision only. Both must be real snapshots that actually exist.
    previous_brief: ManagerBrief | None = None
    current_brief: ManagerBrief | None = None

    def reference_index(self) -> ReferenceIndex:
        return ReferenceIndex.build(self.brief, self.clarification_rounds)

    def asked_question_ids(self) -> set[str]:
        ids: set[str] = set()
        for round_ in self.clarification_rounds:
            ids |= round_.batch.question_ids()
        return ids

    def question_statuses(self) -> dict[str, AnswerStatus]:
        statuses: dict[str, AnswerStatus] = {}
        for round_ in self.clarification_rounds:
            for response in round_.responses:
                statuses[response.question_id] = response.status
        return statuses


# --- Step 1: promotion ----------------------------------------------------


def _promote(action: AdvisoryAction, wire: BaseModel) -> Any:
    """Wire object to strict application contract.

    Field names match by construction, so this is a revalidation rather than a
    translation. Everything the API could not enforce is enforced here.
    """
    contract = output_contract_for(action)
    try:
        return contract.model_validate(wire.model_dump())
    except ValidationError as exc:
        raise OutputRejected(_format_errors(exc)) from exc


def _format_errors(exc: ValidationError) -> list[str]:
    out: list[str] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"]) or "(root)"
        out.append(f"{location}: {error['msg']}")
    return out


# --- Step 2 to 6: the checks ---------------------------------------------


def _check_context(payload: Any, context: ValidationContext, errors: list[str]) -> None:
    expected = context.brief.context_id
    found = getattr(payload, "context_id", None)
    if found is not None and found != expected:
        errors.append(
            f"context_id: output names '{found}' but this session is '{expected}'. "
            "Return the context_id exactly as supplied."
        )


def _check_references(payload: Any, context: ValidationContext, errors: list[str]) -> None:
    index = context.reference_index()
    statuses = context.question_statuses()

    for ref in collect_source_refs(payload):
        if index.resolves(ref):
            continue

        if ref.kind is SourceKind.CLARIFICATION_ANSWER and ref.ref_id in statuses:
            status = statuses[ref.ref_id]
            errors.append(
                f"source {ref}: question {ref.ref_id} is {status.value}, so it produced no "
                "information and nothing may cite it. If this is your own inference, move it "
                "to assumptions."
            )
        else:
            errors.append(f"source {ref}: no such identifier in this session")


def _check_named_initiatives(ids: set[str], brief: ManagerBrief, label: str, errors: list[str]) -> None:
    unknown = sorted(ids - brief.initiative_ids())
    if unknown:
        errors.append(
            f"{label}: names initiatives that are not in the brief: {', '.join(unknown)}"
        )


def _check_clarification(
    payload: ClarificationBatch, context: ValidationContext, errors: list[str]
) -> None:
    already = context.asked_question_ids()
    statuses = context.question_statuses()

    for question in payload.questions:
        if question.id not in already:
            continue
        status = statuses.get(question.id, AnswerStatus.UNANSWERED)
        if status is AnswerStatus.SKIPPED:
            errors.append(
                f"questions: {question.id} was already asked and the manager skipped it. "
                "A declined question is not re-asked."
            )
        else:
            errors.append(f"questions: {question.id} has already been asked in this session")


def _check_comparison(payload: Comparison, context: ValidationContext, errors: list[str]) -> None:
    _check_named_initiatives(payload.compared_ids(), context.brief, "initiatives", errors)

    missing = sorted(context.brief.initiative_ids() - payload.compared_ids())
    if missing:
        errors.append(
            f"initiatives: the brief lists initiatives that were not compared: {', '.join(missing)}. "
            "Compare every option, including any you consider weak."
        )


def _check_recommendation(
    payload: Recommendation, context: ValidationContext, errors: list[str]
) -> None:
    if context.comparison is None:
        errors.append(
            "a recommendation requires a comparison first; none exists in this session"
        )
        return

    _check_named_initiatives(payload.recommended_ids(), context.brief, "items", errors)

    compared = context.comparison.compared_ids()
    recommended = payload.recommended_ids()

    missing = sorted(compared - recommended)
    if missing:
        errors.append(
            f"items: these initiatives were compared but do not appear in the "
            f"recommendation: {', '.join(missing)}"
        )

    extra = sorted(recommended - compared)
    if extra:
        errors.append(
            f"items: these appear in the recommendation but were never compared: {', '.join(extra)}"
        )


def _check_revision(payload: Revision, context: ValidationContext, errors: list[str]) -> None:
    """Revision needs two real snapshots, and its claims checked against them.

    Previously a revision could name any two context identifiers and report a
    change to a constraint that does not exist, and nothing objected. Both are
    now rejected.
    """
    previous = context.previous_brief
    current = context.current_brief

    if previous is None or current is None:
        errors.append(
            "a revision requires both a previous and a current brief snapshot; "
            "this session does not have both"
        )
        return

    if payload.previous_context_id != previous.context_id:
        errors.append(
            f"previous_context_id: output names '{payload.previous_context_id}' but the "
            f"stored previous snapshot is '{previous.context_id}'"
        )
    if payload.current_context_id != current.context_id:
        errors.append(
            f"current_context_id: output names '{payload.current_context_id}' but the "
            f"stored current snapshot is '{current.context_id}'"
        )

    before = {c.id: c.value for c in previous.constraints}
    after = {c.id: c.value for c in current.constraints}

    for change in payload.triggered_by:
        cid = change.constraint_id

        if cid not in before and cid not in after:
            errors.append(
                f"triggered_by: constraint {cid} does not exist in either snapshot"
            )
            continue

        expected_previous = before.get(cid)
        expected_current = after.get(cid)

        if change.previous_value != expected_previous:
            errors.append(
                f"triggered_by: {cid} previous_value is reported as "
                f"{change.previous_value!r} but the previous snapshot holds "
                f"{expected_previous!r}"
            )
        if change.current_value != expected_current:
            errors.append(
                f"triggered_by: {cid} current_value is reported as "
                f"{change.current_value!r} but the current snapshot holds "
                f"{expected_current!r}"
            )

    covered = {c.initiative_id for c in payload.moved} | {c.initiative_id for c in payload.held}
    _check_named_initiatives(covered, current, "moved/held", errors)


# --- Entry point ----------------------------------------------------------


def validate_output(
    action: AdvisoryAction,
    wire: BaseModel,
    context: ValidationContext,
) -> Any:
    """Promote and check one advisory output.

    Returns the strict contract instance on success. Raises
    :class:`OutputRejected` with actionable messages on failure. The caller is
    responsible for never writing to session state except with what this
    returns.
    """
    payload = _promote(action, wire)

    errors: list[str] = []

    _check_context(payload, context, errors)
    _check_references(payload, context, errors)

    if isinstance(payload, ClarificationBatch):
        _check_clarification(payload, context, errors)
    elif isinstance(payload, Comparison):
        _check_comparison(payload, context, errors)
    elif isinstance(payload, Recommendation):
        _check_recommendation(payload, context, errors)
    elif isinstance(payload, Revision):
        _check_revision(payload, context, errors)
    elif isinstance(payload, (Diagnosis, ContextRequest)):
        pass  # context and references already checked above

    if errors:
        raise OutputRejected(errors)

    return payload


def validate_next_action(
    wire: BaseModel,
    permitted: set[AdvisoryAction],
) -> NextAction:
    """Check the selector's choice against what is actually permitted.

    Separate from :func:`validate_output` because a selector choice is not an
    advisory output and never reaches session state. An action outside the
    permitted set is rejected, not quietly substituted.
    """
    try:
        decision = NextAction.model_validate(wire.model_dump())
    except ValidationError as exc:
        raise OutputRejected(_format_errors(exc)) from exc

    if decision.action not in permitted:
        allowed = ", ".join(sorted(a.value for a in permitted))
        raise OutputRejected(
            [
                f"action: '{decision.action.value}' is not available at this point. "
                f"Choose one of: {allowed}."
            ]
        )

    return decision
