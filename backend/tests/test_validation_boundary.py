"""The validation boundary, including the two review findings it was added to close."""

from __future__ import annotations

import pytest

from app.core.validation import (
    OutputRejected,
    ValidationContext,
    validate_next_action,
    validate_output,
)
from app.data import load_sample_brief
from app.models import (
    AdvisoryAction,
    AnswerStatus,
    ClarificationBatch,
    ClarificationResponse,
    ClarificationRound,
    Comparison,
    ManagerBrief,
)
from app.models import wire as w
from tests import doubles


@pytest.fixture()
def brief() -> ManagerBrief:
    return load_sample_brief()


@pytest.fixture()
def context(brief) -> ValidationContext:
    return ValidationContext(brief=brief)


# --- Regression: an unrelated context identifier used to pass ------------


def test_unrelated_context_id_is_rejected(context):
    """Review finding. An output naming another session's context was accepted.

    A comparison carrying a foreign context identifier would previously attach
    to whichever session received it, which is how advice about one situation
    ends up presented as advice about another.
    """
    payload = doubles.comparison(context_id="CTX-SOMEONE-ELSE")

    with pytest.raises(OutputRejected) as caught:
        validate_output(AdvisoryAction.COMPARE, payload, context)

    assert any("context_id" in error for error in caught.value.errors)


def test_matching_context_id_is_accepted(context):
    result = validate_output(AdvisoryAction.COMPARE, doubles.comparison(), context)
    assert result.context_id == context.brief.context_id


def test_diagnosis_context_is_checked_too(context):
    with pytest.raises(OutputRejected, match="context_id"):
        validate_output(AdvisoryAction.DIAGNOSE, doubles.diagnosis("CTX-WRONG"), context)


# --- Regression: a revision naming a nonexistent constraint used to pass --


def _revision(
    *,
    constraint_id: str = "CON-BUDGET",
    previous_value: str | None = None,
    current_value: str | None = None,
    previous_ctx: str = "CTX-LARKFIELD-1",
    current_ctx: str = "CTX-LARKFIELD-2",
) -> w.WireNextAction | dict:
    from app.models import Revision

    return Revision.model_validate(
        {
            "previous_context_id": previous_ctx,
            "current_context_id": current_ctx,
            "triggered_by": [
                {
                    "constraint_id": constraint_id,
                    "previous_value": previous_value,
                    "current_value": current_value,
                }
            ],
            "moved": [],
            "held": [],
            "explanation": "Scripted revision for validation testing.",
            "open_unknowns": [],
            "cross_cutting_notes": [],
        }
    )


def _snapshots(brief: ManagerBrief) -> tuple[ManagerBrief, ManagerBrief]:
    previous = brief.model_copy(deep=True)
    current = brief.model_copy(deep=True)
    current.context_id = "CTX-LARKFIELD-2"
    for constraint in current.constraints:
        if constraint.id == "CON-BUDGET":
            constraint.value = "60,000 EUR after a freeze"
    return previous, current


def test_revision_requires_real_snapshots(brief, context):
    """Without both snapshots there is nothing to check a change against."""
    revision = _revision(
        previous_value="about 150,000 EUR for the first year, including internal time",
        current_value="60,000 EUR after a freeze",
    )

    with pytest.raises(OutputRejected, match="snapshot"):
        validate_output(AdvisoryAction.REVISE, revision, context)


def test_revision_naming_a_nonexistent_constraint_is_rejected(brief):
    """Review finding. A change to a constraint that does not exist was accepted."""
    previous, current = _snapshots(brief)
    context = ValidationContext(brief=current, previous_brief=previous, current_brief=current)

    revision = _revision(
        constraint_id="CON-INVENTED",
        previous_value="something",
        current_value="something else",
    )

    with pytest.raises(OutputRejected) as caught:
        validate_output(AdvisoryAction.REVISE, revision, context)

    assert any("does not exist in either snapshot" in error for error in caught.value.errors)


def test_revision_misreporting_a_value_is_rejected(brief):
    """A real constraint, but values that do not match the snapshots."""
    previous, current = _snapshots(brief)
    context = ValidationContext(brief=current, previous_brief=previous, current_brief=current)

    revision = _revision(
        previous_value="a figure nobody ever stated",
        current_value="60,000 EUR after a freeze",
    )

    with pytest.raises(OutputRejected) as caught:
        validate_output(AdvisoryAction.REVISE, revision, context)

    assert any("previous_value" in error for error in caught.value.errors)


def test_revision_matching_the_snapshots_is_accepted(brief):
    previous, current = _snapshots(brief)
    context = ValidationContext(brief=current, previous_brief=previous, current_brief=current)

    revision = _revision(
        previous_value="about 150,000 EUR for the first year, including internal time",
        current_value="60,000 EUR after a freeze",
    )

    accepted = validate_output(AdvisoryAction.REVISE, revision, context)
    assert accepted.triggered_by[0].constraint_id == "CON-BUDGET"


# --- References and initiatives -------------------------------------------


def test_comparison_naming_an_unknown_initiative_is_rejected(context):
    payload = doubles.comparison(initiative_ids=["INI-ROUTE", "INI-DOCS", "INI-GHOST"])

    with pytest.raises(OutputRejected) as caught:
        validate_output(AdvisoryAction.COMPARE, payload, context)

    assert any("INI-GHOST" in error for error in caught.value.errors)


def test_comparison_omitting_an_initiative_is_rejected(context):
    payload = doubles.comparison(initiative_ids=["INI-ROUTE", "INI-DOCS"])

    with pytest.raises(OutputRejected) as caught:
        validate_output(AdvisoryAction.COMPARE, payload, context)

    assert any("not compared" in error for error in caught.value.errors)


def test_citing_a_skipped_question_is_rejected(brief):
    """A skipped question produced no information, so nothing may rest on it."""
    round_ = ClarificationRound(
        batch=ClarificationBatch(
            questions=[
                {
                    "id": "Q-DATA",
                    "question": "Does historical data exist?",
                    "why_it_matters": "It decides the size of the project.",
                }
            ]
        ),
        responses=[
            ClarificationResponse(
                question_id="Q-DATA", status=AnswerStatus.SKIPPED, answer=None
            )
        ],
    )
    context = ValidationContext(brief=brief, clarification_rounds=[round_])

    payload = doubles.comparison()
    payload.initiatives[0].stated_facts.append(
        w.WireClaim(
            statement="The manager confirmed the data exists.",
            sources=[w.WireSourceRef(kind="clarification.answer", ref_id="Q-DATA")],
        )
    )

    with pytest.raises(OutputRejected) as caught:
        validate_output(AdvisoryAction.COMPARE, payload, context)

    assert any("skipped" in error for error in caught.value.errors)


def test_re_asking_a_skipped_question_is_rejected(brief):
    round_ = ClarificationRound(
        batch=ClarificationBatch(
            questions=[
                {
                    "id": "Q-DATA",
                    "question": "Does historical data exist?",
                    "why_it_matters": "It decides the size of the project.",
                }
            ]
        ),
        responses=[
            ClarificationResponse(
                question_id="Q-DATA", status=AnswerStatus.SKIPPED, answer=None
            )
        ],
    )
    context = ValidationContext(brief=brief, clarification_rounds=[round_])

    with pytest.raises(OutputRejected) as caught:
        validate_output(
            AdvisoryAction.ASK_CLARIFICATION, doubles.clarification(["Q-DATA"]), context
        )

    assert any("skipped" in error for error in caught.value.errors)


def test_more_than_three_questions_is_rejected_by_the_application(context):
    """The API cannot enforce this. The wire object is valid; the contract is not.

    This is the whole reason the two layers exist.
    """
    oversized = w.WireClarificationBatch(
        questions=[
            w.WireClarificationQuestion(
                id=f"Q-{n}", question="Scripted?", why_it_matters="It matters.", relates_to=[]
            )
            for n in range(1, 5)
        ]
    )
    assert len(oversized.questions) == 4  # valid on the wire

    with pytest.raises(OutputRejected):
        validate_output(AdvisoryAction.ASK_CLARIFICATION, oversized, context)


# --- Prior outputs --------------------------------------------------------


def test_recommendation_without_a_comparison_is_rejected(context):
    with pytest.raises(OutputRejected) as caught:
        validate_output(AdvisoryAction.RECOMMEND, doubles.recommendation(), context)

    assert any("requires a comparison" in error for error in caught.value.errors)


def test_recommendation_must_cover_every_compared_initiative(brief):
    comparison = Comparison.model_validate(doubles.comparison().model_dump())
    context = ValidationContext(brief=brief, comparison=comparison)

    partial = doubles.recommendation(initiative_ids=["INI-DOCS", "INI-ROUTE"])

    with pytest.raises(OutputRejected) as caught:
        validate_output(AdvisoryAction.RECOMMEND, partial, context)

    assert any("do not appear in the recommendation" in error for error in caught.value.errors)


def test_recommendation_covering_the_comparison_is_accepted(brief):
    comparison = Comparison.model_validate(doubles.comparison().model_dump())
    context = ValidationContext(brief=brief, comparison=comparison)

    accepted = validate_output(AdvisoryAction.RECOMMEND, doubles.recommendation(), context)
    assert len(accepted.items) == 3


# --- Selector -------------------------------------------------------------


def test_selector_choosing_an_unpermitted_action_is_rejected():
    with pytest.raises(OutputRejected) as caught:
        validate_next_action(
            doubles.next_action("recommend"), permitted={AdvisoryAction.DIAGNOSE}
        )

    assert any("not available" in error for error in caught.value.errors)


def test_selector_choosing_an_unknown_action_is_rejected():
    with pytest.raises(OutputRejected):
        validate_next_action(
            doubles.next_action("escalate_to_finance"), permitted={AdvisoryAction.DIAGNOSE}
        )


def test_selector_choosing_a_permitted_action_is_accepted():
    decision = validate_next_action(
        doubles.next_action("diagnose"),
        permitted={AdvisoryAction.DIAGNOSE, AdvisoryAction.AWAIT_USER},
    )
    assert decision.action is AdvisoryAction.DIAGNOSE
