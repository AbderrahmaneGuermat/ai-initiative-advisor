"""Validates the hand-authored worked example against the contracts.

What passing proves: the sample payloads have the declared shape, and every
identifier they cite exists in the brief or in an answered clarification
question.

What passing does not prove: that the analysis is sound, that the recommendation
is right, or that any claim filed under stated facts is a fact. The example was
written by a person to exercise the contracts. It is not model output, and no
model has run in this project. See backend/app/data/README.md.
"""

from __future__ import annotations

from app.models import (
    AnswerStatus,
    ClarificationRound,
    Comparison,
    ManagerBrief,
    Recommendation,
    ReferenceIndex,
    Revision,
    Stance,
    known_initiative_ids_only,
    require_resolvable_references,
)


def test_brief_validates(brief_payload):
    brief = ManagerBrief.model_validate(brief_payload)
    assert brief.context_id == "CTX-LARKFIELD-1"
    assert len(brief.initiatives) == 3


def test_brief_is_deliberately_incomplete(brief_payload):
    """The gaps are the point of the scenario, so they are pinned here.

    If someone later 'tidies' the sample by filling these in, the worked example
    stops demonstrating what it exists to demonstrate.
    """
    brief = ManagerBrief.model_validate(brief_payload)

    objectives = {o.id: o for o in brief.objectives}
    assert objectives["OBJ-COST"].rationale is None

    constraints = {c.id: c for c in brief.constraints}
    assert constraints["CON-TEAM"].value is None

    initiatives = {i.id: i for i in brief.initiatives}
    assert initiatives["INI-CHAT"].description is None


def test_clarification_round_validates_and_keeps_the_skip(clarification_payload):
    round_ = ClarificationRound.model_validate(clarification_payload)

    assert len(round_.batch.questions) == 3
    assert round_.answered_ids() == {"Q-VOLUME"}

    statuses = {r.question_id: r.status for r in round_.responses}
    assert statuses["Q-DATA"] is AnswerStatus.SKIPPED
    assert statuses["Q-TEAM"] is AnswerStatus.UNANSWERED

    assert {r.question_id for r in round_.open_questions()} == {"Q-DATA", "Q-TEAM"}


def test_comparison_validates_and_resolves(brief_payload, clarification_payload, comparison_payload):
    brief = ManagerBrief.model_validate(brief_payload)
    round_ = ClarificationRound.model_validate(clarification_payload)
    index = ReferenceIndex.build(brief, [round_])

    comparison = Comparison.model_validate(comparison_payload)
    require_resolvable_references(comparison, index)

    assert comparison.compared_ids() == brief.initiative_ids()


def test_the_skipped_question_became_missing_evidence_not_a_low_rating(comparison_payload):
    """The behaviour the whole qualitative design exists to produce.

    The manager skipped the question about historical data. In a weighted model
    that unknown would have to become a number. Here it is an entry under
    missing_evidence for the initiative it affects, and nothing else.
    """
    comparison = Comparison.model_validate(comparison_payload)
    route = next(i for i in comparison.initiatives if i.initiative_id == "INI-ROUTE")

    descriptions = " ".join(m.description.lower() for m in route.missing_evidence)
    assert "historical" in descriptions

    for item in route.missing_evidence:
        assert item.why_it_matters.strip()


def test_assumptions_carry_no_sources_and_facts_do(comparison_payload):
    """A structural property of the example, not a claim about truth.

    Stated facts point at an input; assumptions do not. That is the convention
    the example follows and what makes the two visibly different to a reader.
    Nothing here establishes that the facts are true.
    """
    comparison = Comparison.model_validate(comparison_payload)

    for initiative in comparison.initiatives:
        for assumption in initiative.assumptions:
            assert assumption.sources == [], (
                f"{initiative.initiative_id}: an assumption cites an input, "
                "which blurs the distinction the example is meant to show"
            )
        for fact in initiative.stated_facts:
            assert fact.sources, (
                f"{initiative.initiative_id}: a stated fact cites nothing, "
                "so it cannot be traced back to the manager's input"
            )


def test_recommendation_validates_and_names_only_known_initiatives(
    brief_payload, clarification_payload, recommendation_payload
):
    brief = ManagerBrief.model_validate(brief_payload)
    round_ = ClarificationRound.model_validate(clarification_payload)
    index = ReferenceIndex.build(brief, [round_])

    recommendation = Recommendation.model_validate(recommendation_payload)
    require_resolvable_references(recommendation, index)

    assert known_initiative_ids_only(recommendation.recommended_ids(), index) == []


def test_recommendation_carries_the_skipped_question_forward(recommendation_payload):
    """A skipped answer must still be visible in the advice that follows it."""
    recommendation = Recommendation.model_validate(recommendation_payload)

    unknowns = " ".join(recommendation.open_unknowns).lower()
    assert "historical" in unknowns
    assert "skipped" in unknowns


def test_undescribed_initiative_is_not_rejected_on_the_strength_of_its_name(
    recommendation_payload,
):
    """INI-CHAT has a name and no description.

    The example files it as insufficient_information rather than
    not_recommended. The distinction matters: rejecting an option nobody has
    specified would be a judgement about a title.
    """
    recommendation = Recommendation.model_validate(recommendation_payload)
    chat = next(i for i in recommendation.items if i.initiative_id == "INI-CHAT")
    assert chat.stance is Stance.INSUFFICIENT_INFORMATION


def test_revision_validates_and_explains_what_moved_and_what_held(
    brief_payload, clarification_payload, revision_payload
):
    brief = ManagerBrief.model_validate(brief_payload)
    round_ = ClarificationRound.model_validate(clarification_payload)
    index = ReferenceIndex.build(brief, [round_])

    revision = Revision.model_validate(revision_payload)
    require_resolvable_references(revision, index)

    assert revision.previous_context_id == "CTX-LARKFIELD-1"
    assert revision.current_context_id == "CTX-LARKFIELD-2"

    moved = {c.initiative_id for c in revision.moved}
    held = {c.initiative_id for c in revision.held}

    assert moved == {"INI-ROUTE"}
    assert held == {"INI-DOCS", "INI-CHAT"}
    assert moved | held == brief.initiative_ids(), "every initiative is accounted for"


def test_revision_carries_its_unknowns_through(revision_payload):
    """A changed constraint resolves nothing that was unknown before it."""
    revision = Revision.model_validate(revision_payload)
    unknowns = " ".join(revision.open_unknowns).lower()
    assert "historical" in unknowns
    assert len(revision.open_unknowns) >= 5


def test_every_initiative_in_the_advice_exists_in_the_brief(
    brief_payload, comparison_payload, recommendation_payload, revision_payload
):
    """One check across the whole worked example."""
    brief = ManagerBrief.model_validate(brief_payload)
    known = brief.initiative_ids()

    comparison = Comparison.model_validate(comparison_payload)
    recommendation = Recommendation.model_validate(recommendation_payload)
    revision = Revision.model_validate(revision_payload)

    referenced = (
        comparison.compared_ids()
        | recommendation.recommended_ids()
        | {c.initiative_id for c in revision.moved}
        | {c.initiative_id for c in revision.held}
    )
    assert referenced <= known, f"advice names initiatives not in the brief: {referenced - known}"
