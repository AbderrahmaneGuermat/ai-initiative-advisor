"""Tests for the contract boundaries.

These check structure and referential integrity, which is all the contracts
claim to enforce. Nothing here asserts that a comparison is sound or that a
recommendation is wise. Those are judgements, they belong to the prompts and to
the reviewing manager, and a test that pretended to check them would be
checking a keyword list instead.
"""

from __future__ import annotations

import typing
from decimal import Decimal
from enum import Enum

import pytest
from pydantic import BaseModel, ValidationError

from app.models import (
    ACTION_OUTPUT_CONTRACTS,
    MAX_QUESTIONS_PER_BATCH,
    AdvisoryAction,
    AnswerStatus,
    ClarificationBatch,
    ClarificationResponse,
    ClarificationRound,
    Comparison,
    ManagerBrief,
    NextAction,
    Recommendation,
    ReferenceIndex,
    Revision,
    SourceKind,
    SourceRef,
    Stance,
    UnresolvedReferenceError,
    known_initiative_ids_only,
    output_contract_for,
    require_resolvable_references,
    unresolved_references,
)


# --- The action contract --------------------------------------------------


def test_unknown_action_is_rejected():
    """An action outside the permitted set fails, rather than passing through."""
    with pytest.raises(ValidationError):
        NextAction(action="escalate_to_finance", reasoning="the budget looks wrong")


def test_known_action_is_accepted():
    decision = NextAction(action="ask_clarification", reasoning="Volume is unknown and decides it.")
    assert decision.action is AdvisoryAction.ASK_CLARIFICATION


def test_next_action_requires_reasoning():
    """Reasoning is not optional. An adaptive loop with no stated why is unreviewable."""
    with pytest.raises(ValidationError):
        NextAction(action="compare", reasoning="   ")


def test_next_action_rejects_undeclared_fields():
    with pytest.raises(ValidationError):
        NextAction(action="compare", reasoning="enough is known", confidence=0.8)


def test_every_action_declares_an_output_contract():
    """Guards against the drift that made the diagnosis prompt unreachable.

    An action added without a contract fails here rather than at runtime. See
    docs/decisions.md, D-017.
    """
    missing = [a for a in AdvisoryAction if a not in ACTION_OUTPUT_CONTRACTS]
    assert missing == [], f"actions with no declared output contract: {missing}"

    for action in AdvisoryAction:
        assert output_contract_for(action) is ACTION_OUTPUT_CONTRACTS[action]


def test_diagnose_is_a_permitted_action():
    """The specific mismatch this iteration was asked to resolve."""
    assert AdvisoryAction.DIAGNOSE in ACTION_OUTPUT_CONTRACTS


# --- Clarification limits -------------------------------------------------


def _question(qid: str) -> dict:
    return {"id": qid, "question": f"Question {qid}?", "why_it_matters": "It changes the advice."}


def test_batch_rejects_more_than_three_questions():
    with pytest.raises(ValidationError):
        ClarificationBatch(questions=[_question(f"Q-{n}") for n in range(1, 5)])


def test_batch_accepts_exactly_three():
    batch = ClarificationBatch(questions=[_question(f"Q-{n}") for n in range(1, 4)])
    assert len(batch.questions) == MAX_QUESTIONS_PER_BATCH


def test_batch_rejects_an_empty_set_of_questions():
    """Asking nothing is not a clarification. It is a different action."""
    with pytest.raises(ValidationError):
        ClarificationBatch(questions=[])


def test_batch_rejects_duplicate_question_ids():
    with pytest.raises(ValidationError):
        ClarificationBatch(questions=[_question("Q-A"), _question("Q-A")])


# --- Answered, skipped and unanswered ------------------------------------


def test_answered_question_must_carry_an_answer():
    with pytest.raises(ValidationError):
        ClarificationResponse(question_id="Q-A", status=AnswerStatus.ANSWERED, answer=None)


@pytest.mark.parametrize("status", [AnswerStatus.SKIPPED, AnswerStatus.UNANSWERED])
def test_unanswered_question_must_not_carry_an_answer(status):
    """Nothing may be attributed to a manager who did not reply."""
    with pytest.raises(ValidationError):
        ClarificationResponse(question_id="Q-A", status=status, answer="probably around 400")


def test_every_question_needs_a_response_entry():
    """An untouched question stays present. Absence would be indistinguishable
    from never having been asked."""
    with pytest.raises(ValidationError):
        ClarificationRound(
            batch={"questions": [_question("Q-A"), _question("Q-B")]},
            responses=[{"question_id": "Q-A", "status": "answered", "answer": "400 a week"}],
        )


def test_response_cannot_reference_a_question_that_was_not_asked():
    with pytest.raises(ValidationError):
        ClarificationRound(
            batch={"questions": [_question("Q-A")]},
            responses=[
                {"question_id": "Q-A", "status": "unanswered", "answer": None},
                {"question_id": "Q-ELSEWHERE", "status": "answered", "answer": "yes"},
            ],
        )


def test_skipped_and_unanswered_are_kept_distinct_and_both_stay_open():
    round_ = ClarificationRound(
        batch={"questions": [_question("Q-A"), _question("Q-B"), _question("Q-C")]},
        responses=[
            {"question_id": "Q-A", "status": "answered", "answer": "400 a week"},
            {"question_id": "Q-B", "status": "skipped", "answer": None},
            {"question_id": "Q-C", "status": "unanswered", "answer": None},
        ],
    )

    assert round_.answered_ids() == {"Q-A"}

    open_ids = {r.question_id for r in round_.open_questions()}
    assert open_ids == {"Q-B", "Q-C"}

    statuses = {r.question_id: r.status for r in round_.responses}
    assert statuses["Q-B"] is AnswerStatus.SKIPPED
    assert statuses["Q-C"] is AnswerStatus.UNANSWERED


def test_a_skipped_question_is_not_a_citable_source():
    """A skipped question produced no input, so nothing may rest on it."""
    round_ = ClarificationRound(
        batch={"questions": [_question("Q-A")]},
        responses=[{"question_id": "Q-A", "status": "skipped", "answer": None}],
    )
    assert "Q-A" not in round_.answered_ids()


# --- Brief integrity ------------------------------------------------------


def test_brief_rejects_duplicate_initiative_ids():
    with pytest.raises(ValidationError):
        ManagerBrief(
            context_id="CTX-X",
            organisation="Fictional Co",
            situation=None,
            initiatives=[
                {"id": "INI-A", "name": "One", "description": None},
                {"id": "INI-A", "name": "Two", "description": None},
            ],
        )


def test_brief_rejects_an_initiative_claiming_an_unknown_objective():
    with pytest.raises(ValidationError):
        ManagerBrief(
            context_id="CTX-X",
            organisation="Fictional Co",
            situation=None,
            objectives=[{"id": "OBJ-A", "statement": "Reduce cost", "rationale": None}],
            initiatives=[
                {
                    "id": "INI-A",
                    "name": "One",
                    "description": None,
                    "claimed_objectives": ["OBJ-MISSING"],
                }
            ],
        )


def test_an_incomplete_brief_is_valid():
    """A thin brief is the normal starting point, not an error.

    Noticing that it is thin is the advisor's job. A validator that rejected it
    would be making a judgement, which is what these contracts must not do.
    """
    brief = ManagerBrief(
        context_id="CTX-X",
        organisation="Fictional Co",
        situation=None,
        objectives=[{"id": "OBJ-A", "statement": "Reduce cost", "rationale": None}],
        constraints=[{"id": "CON-A", "kind": "budget", "value": None}],
        initiatives=[{"id": "INI-A", "name": "Something", "description": None}],
    )
    assert brief.constraints[0].value is None
    assert brief.initiatives[0].description is None


def test_identifier_prefixes_are_enforced():
    with pytest.raises(ValidationError):
        ManagerBrief(
            context_id="CTX-X",
            organisation="Fictional Co",
            situation=None,
            initiatives=[{"id": "initiative-1", "name": "Wrong prefix", "description": None}],
        )


# --- Reference resolution -------------------------------------------------


@pytest.fixture()
def small_index() -> ReferenceIndex:
    brief = ManagerBrief(
        context_id="CTX-X",
        organisation="Fictional Co",
        situation=None,
        objectives=[{"id": "OBJ-A", "statement": "Reduce cost", "rationale": None}],
        constraints=[{"id": "CON-A", "kind": "budget", "value": "100k"}],
        initiatives=[{"id": "INI-A", "name": "Something", "description": None}],
    )
    round_ = ClarificationRound(
        batch={"questions": [_question("Q-A"), _question("Q-B")]},
        responses=[
            {"question_id": "Q-A", "status": "answered", "answer": "400 a week"},
            {"question_id": "Q-B", "status": "skipped", "answer": None},
        ],
    )
    return ReferenceIndex.build(brief, [round_])


def test_invalid_reference_is_detected(small_index):
    comparison = Comparison(
        context_id="CTX-X",
        initiatives=[
            {
                "initiative_id": "INI-A",
                "stated_facts": [
                    {
                        "statement": "Cited input does not exist.",
                        "sources": [{"kind": "brief.objective", "ref_id": "OBJ-NOPE"}],
                    }
                ],
            }
        ],
    )

    unresolved = unresolved_references(comparison, small_index)
    assert [r.ref_id for r in unresolved] == ["OBJ-NOPE"]

    with pytest.raises(UnresolvedReferenceError):
        require_resolvable_references(comparison, small_index)


def test_reference_to_a_skipped_answer_does_not_resolve(small_index):
    """Q-B was asked and skipped, so it is not citable."""
    assert small_index.resolves(SourceRef(kind=SourceKind.CLARIFICATION_ANSWER, ref_id="Q-A"))
    assert not small_index.resolves(SourceRef(kind=SourceKind.CLARIFICATION_ANSWER, ref_id="Q-B"))


def test_reference_of_the_wrong_kind_does_not_resolve(small_index):
    """Identifier namespaces do not leak into one another."""
    assert not small_index.resolves(SourceRef(kind=SourceKind.OBJECTIVE, ref_id="INI-A"))


def test_resolution_is_structural_only(small_index):
    """A citation pointing at an unrelated input still passes.

    This test exists to pin the limit of the check, per docs/decisions.md D-016.
    The reference below is real and the claim it supports is nonsense. Nothing
    in the contracts detects that, and nothing should pretend to.
    """
    comparison = Comparison(
        context_id="CTX-X",
        initiatives=[
            {
                "initiative_id": "INI-A",
                "stated_facts": [
                    {
                        "statement": "The budget constraint proves this initiative will succeed.",
                        "sources": [{"kind": "brief.constraint", "ref_id": "CON-A"}],
                    }
                ],
            }
        ],
    )
    assert unresolved_references(comparison, small_index) == []


def test_recommendation_naming_an_unknown_initiative_is_detected(small_index):
    recommendation = Recommendation(
        context_id="CTX-X",
        summary="Proceed with something that is not in the brief.",
        items=[
            {
                "initiative_id": "INI-GHOST",
                "stance": Stance.RECOMMENDED,
                "rationale": "Invented.",
            }
        ],
        open_unknowns=[],
        confidence_note="Low.",
    )
    unknown = known_initiative_ids_only(recommendation.recommended_ids(), small_index)
    assert unknown == ["INI-GHOST"]


# --- Structural rules on advice and revision ------------------------------


def test_revision_requires_two_different_contexts():
    with pytest.raises(ValidationError):
        Revision(
            previous_context_id="CTX-A",
            current_context_id="CTX-A",
            triggered_by=[
                {"constraint_id": "CON-A", "previous_value": "100k", "current_value": "60k"}
            ],
            explanation="Nothing can be stated against itself.",
            open_unknowns=[],
        )


def test_revision_rejects_a_trigger_where_nothing_changed():
    with pytest.raises(ValidationError):
        Revision(
            previous_context_id="CTX-A",
            current_context_id="CTX-B",
            triggered_by=[
                {"constraint_id": "CON-A", "previous_value": "100k", "current_value": "100k"}
            ],
            explanation="The trigger did not trigger.",
            open_unknowns=[],
        )


def test_revision_rejects_a_held_item_whose_stance_changed():
    with pytest.raises(ValidationError):
        Revision(
            previous_context_id="CTX-A",
            current_context_id="CTX-B",
            triggered_by=[
                {"constraint_id": "CON-A", "previous_value": "100k", "current_value": "60k"}
            ],
            held=[
                {
                    "initiative_id": "INI-A",
                    "previous_stance": "recommended",
                    "current_stance": "not_recommended",
                    "reason": "Mislabelled as held.",
                }
            ],
            explanation="Held and moved must mean what they say.",
            open_unknowns=[],
        )


def test_revision_rejects_an_initiative_both_moved_and_held():
    with pytest.raises(ValidationError):
        Revision(
            previous_context_id="CTX-A",
            current_context_id="CTX-B",
            triggered_by=[
                {"constraint_id": "CON-A", "previous_value": "100k", "current_value": "60k"}
            ],
            moved=[
                {
                    "initiative_id": "INI-A",
                    "previous_stance": "recommended",
                    "current_stance": "not_recommended",
                    "reason": "Cut.",
                }
            ],
            held=[
                {
                    "initiative_id": "INI-A",
                    "previous_stance": "recommended",
                    "current_stance": "recommended",
                    "reason": "Also held, somehow.",
                }
            ],
            explanation="Contradictory.",
            open_unknowns=[],
        )


def test_recommendation_must_state_its_open_unknowns_field():
    """The field is required, so producing advice means addressing it.

    An empty list is permitted and means "nothing is open", which is a claim a
    reviewer can challenge. Omitting the field entirely is not permitted,
    because that would let advice look complete by saying nothing.
    """
    with pytest.raises(ValidationError):
        Recommendation(
            context_id="CTX-A",
            summary="Do the thing.",
            items=[{"initiative_id": "INI-A", "stance": "recommended", "rationale": "Because."}],
            confidence_note="High.",
        )


def _annotation_types(annotation: object) -> list[object]:
    """Every type mentioned anywhere in an annotation, however nested."""
    seen: set[int] = set()
    pending = [annotation]
    found: list[object] = []
    while pending:
        item = pending.pop()
        if item is None or id(item) in seen:
            continue
        seen.add(id(item))
        found.append(item)
        pending.extend(typing.get_args(item))
    return found


def _numeric_fields(model: type[BaseModel], path: str, visited: set[type]) -> list[str]:
    if model in visited:
        return []
    visited.add(model)

    offenders: list[str] = []
    for name, field in model.model_fields.items():
        mentioned = _annotation_types(field.annotation)
        for candidate in mentioned:
            if not isinstance(candidate, type):
                continue
            if issubclass(candidate, bool) or issubclass(candidate, Enum):
                continue
            if issubclass(candidate, (int, float, Decimal)):
                offenders.append(f"{path}.{name}")
                break
        for candidate in mentioned:
            if isinstance(candidate, type) and issubclass(candidate, BaseModel):
                offenders.extend(_numeric_fields(candidate, f"{path}.{name}", visited))
    return offenders


def test_no_contract_accepts_a_numeric_score():
    """No scoring crept back in under another name.

    Priority is list order plus a coarse stance. Nothing in these contracts, at
    any depth, accepts a number. If a future change adds one, this fails and the
    change has to be argued for rather than slipped in. See docs/decisions.md,
    D-003.

    Enum members are exempt: a str-valued enum is a closed vocabulary, not a
    measurement. Booleans are exempt for the same reason, though none is used.
    """
    offenders: list[str] = []
    visited: set[type] = set()
    for action, contract in ACTION_OUTPUT_CONTRACTS.items():
        offenders.extend(_numeric_fields(contract, f"{action.value}:{contract.__name__}", visited))

    assert offenders == [], f"numeric fields found in output contracts: {offenders}"
