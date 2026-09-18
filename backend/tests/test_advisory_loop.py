"""The bounded advisory loop, with a deterministic double in place of the provider."""

from __future__ import annotations

import asyncio

import openai
import pytest

from app.core.advisory import AdvisoryEngine, permitted_actions
from app.core.limits import Limits
from app.core.model_client import (
    ModelAuthError,
    ModelNotConfigured,
    ModelRateLimited,
    ModelRefused,
    ModelTimeout,
)
from app.data import load_sample_brief
from app.models import AdvisoryAction, AnswerStatus
from app.store.session import SessionStateError, SessionStore
from tests import doubles


def run(coro):
    return asyncio.run(coro)


@pytest.fixture()
def session():
    return SessionStore().create(load_sample_brief())


# --- The happy path -------------------------------------------------------


def test_full_flow_from_diagnosis_to_recommendation(session):
    """Diagnose, clarify, pause. Then answers, compare, recommend."""
    client = doubles.ScriptedClient(
        [
            doubles.next_action("diagnose"),
            doubles.diagnosis(),
            doubles.next_action("ask_clarification"),
            doubles.clarification(),
        ]
    )
    engine = AdvisoryEngine(client)

    first = run(engine.run_turn(session))

    assert first.actions == ["diagnose", "ask_clarification"]
    assert first.awaiting_user is True
    assert session.diagnosis is not None
    assert len(session.all_questions()) == 3
    assert session.comparison is None

    # The manager answers one, skips one, leaves one alone.
    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"})

    client.queue(
        doubles.next_action("compare"),
        doubles.comparison(),
        doubles.next_action("recommend"),
        doubles.recommendation(),
    )

    second = run(engine.run_turn(session))

    assert second.actions == ["compare", "recommend"]
    assert second.stopped_because == "recommendation ready"
    assert session.comparison is not None
    assert session.recommendation is not None
    assert second.error is None


def test_await_user_makes_no_extra_model_call(session):
    """The pause is free. Generating a sentence to say 'waiting' would not be."""
    client = doubles.ScriptedClient([doubles.next_action("await_user")])
    result = run(AdvisoryEngine(client).run_turn(session))

    assert result.awaiting_user is True
    assert result.actions == ["await_user"]
    # One request: the selector. No action call was made.
    assert len(client.calls) == 1
    assert result.budget["model_requests"] == 1


def test_selector_and_repair_calls_count_against_the_budget(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("diagnose"), doubles.diagnosis(), doubles.next_action("await_user")]
    )
    result = run(AdvisoryEngine(client).run_turn(session))

    # Two selector calls plus one action call.
    assert result.budget["model_requests"] == 3
    assert result.budget["actions_taken"] == 1


# --- Answers belong to the manager ---------------------------------------


def test_skipped_and_unanswered_questions_survive_in_session_state(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))

    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"})

    statuses = {qid: status for qid, _q, _w, status in session.all_questions()}
    assert statuses["Q-VOLUME"] is AnswerStatus.ANSWERED
    assert statuses["Q-DATA"] is AnswerStatus.SKIPPED
    assert statuses["Q-TEAM"] is AnswerStatus.UNANSWERED

    open_ids = {qid for qid, _q, _w, _s in session.open_questions()}
    assert open_ids == {"Q-DATA", "Q-TEAM"}


def test_advisory_output_cannot_create_or_alter_an_answer(session):
    """A recommendation that omits a skipped question does not erase it.

    The interface reads questions from session state, so what the model says
    about them changes nothing.
    """
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA", "Q-TEAM"})

    client.queue(
        doubles.next_action("compare"),
        doubles.comparison(),
        doubles.next_action("recommend"),
        # An output claiming there are no open unknowns at all.
        doubles.recommendation(open_unknowns=["Nothing outstanding."]),
    )
    run(engine.run_turn(session))

    assert len(session.open_questions()) == 2
    statuses = {qid: status for qid, _q, _w, status in session.all_questions()}
    assert statuses["Q-DATA"] is AnswerStatus.SKIPPED


def test_answers_for_questions_never_asked_are_rejected(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))

    with pytest.raises(SessionStateError, match="no such question"):
        session.record_answers({"Q-INVENTED": "Something."}, skipped=set())


def test_a_later_submission_does_not_erase_an_earlier_answer(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))

    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped=set())
    session.record_answers({"Q-TEAM": "The operations director."}, skipped=set())

    statuses = {qid: status for qid, _q, _w, status in session.all_questions()}
    assert statuses["Q-VOLUME"] is AnswerStatus.ANSWERED
    assert statuses["Q-TEAM"] is AnswerStatus.ANSWERED


# --- Repair ---------------------------------------------------------------


def test_one_repair_attempt_is_made_and_succeeds(session):
    client = doubles.ScriptedClient(
        [
            doubles.next_action("compare"),
            doubles.comparison(context_id="CTX-WRONG"),  # rejected
            doubles.comparison(),  # the repair
            doubles.next_action("await_user"),
        ]
    )
    result = run(AdvisoryEngine(client).run_turn(session))

    assert session.comparison is not None
    assert result.error is None

    repaired = [trace for trace in result.traces if trace.get("repaired")]
    assert len(repaired) == 1
    assert any("context_id" in error for error in repaired[0]["original_errors"])


def test_a_failed_repair_is_not_retried_and_nothing_is_committed(session):
    """One attempt, then stop. No second repair, no weaker fallback."""
    client = doubles.ScriptedClient(
        [
            doubles.next_action("compare"),
            doubles.comparison(context_id="CTX-WRONG"),
            doubles.comparison(context_id="CTX-STILL-WRONG"),
        ]
    )
    result = run(AdvisoryEngine(client).run_turn(session))

    assert session.comparison is None
    assert result.error is not None
    assert result.error["kind"] == "invalid_output"
    # Selector, action, one repair. Not two.
    assert result.budget["model_requests"] == 3


def test_invalid_output_does_not_replace_previously_validated_advice(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("compare"), doubles.comparison(), doubles.next_action("await_user")]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    good = session.comparison
    assert good is not None

    client.queue(
        doubles.next_action("compare"),
        doubles.comparison(context_id="CTX-WRONG"),
        doubles.comparison(context_id="CTX-WRONG-AGAIN"),
    )
    result = run(engine.run_turn(session))

    assert result.error is not None
    assert session.comparison is good  # untouched


# --- Limits ---------------------------------------------------------------


def test_the_request_budget_stops_the_loop(session):
    limits = Limits(max_model_requests=2, max_actions=10)
    client = doubles.ScriptedClient(
        [
            doubles.next_action("diagnose"),
            doubles.diagnosis(),
            doubles.next_action("compare"),
            doubles.comparison(),
        ]
    )
    result = run(AdvisoryEngine(client, limits=limits).run_turn(session))

    assert result.error is not None
    assert result.error["kind"] == "limit"
    assert result.error["limit"] == "max_model_requests"
    assert len(client.calls) == 2


def test_the_action_budget_stops_the_loop(session):
    limits = Limits(max_actions=1, max_model_requests=20)
    client = doubles.ScriptedClient(
        [
            doubles.next_action("diagnose"),
            doubles.diagnosis(),
            doubles.next_action("compare"),
            doubles.comparison(),
        ]
    )
    result = run(AdvisoryEngine(client, limits=limits).run_turn(session))

    assert result.error["limit"] == "max_actions"
    assert result.budget["actions_taken"] == 1


def test_oversized_input_is_refused_before_the_request_is_made(session):
    limits = Limits(max_input_chars=50)
    client = doubles.ScriptedClient([doubles.next_action("diagnose")])
    result = run(AdvisoryEngine(client, limits=limits).run_turn(session))

    assert result.error["limit"] == "max_input_chars"
    assert client.calls == []  # nothing was sent


# --- Provider failures ----------------------------------------------------


@pytest.mark.parametrize(
    "failure,expected_kind,recoverable",
    [
        (ModelRateLimited("429"), "ModelRateLimited", True),
        (ModelTimeout("timed out"), "ModelTimeout", True),
        (ModelAuthError("bad key"), "ModelAuthError", False),
        (ModelRefused("declined"), "ModelRefused", False),
    ],
)
def test_provider_failures_surface_and_commit_nothing(
    session, failure, expected_kind, recoverable
):
    """A failure is reported as a failure. Never replaced with sample output."""
    client = doubles.ScriptedClient([doubles.next_action("diagnose"), failure])
    result = run(AdvisoryEngine(client).run_turn(session))

    assert result.error is not None
    assert result.error["kind"] == expected_kind
    assert result.error["recoverable"] is recoverable
    assert session.diagnosis is None
    assert session.records == []


def test_session_is_usable_again_after_a_recoverable_failure(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("diagnose"), ModelRateLimited("429")]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    assert session.status == "ready"

    client.queue(
        doubles.next_action("diagnose"), doubles.diagnosis(), doubles.next_action("await_user")
    )
    result = run(engine.run_turn(session))

    assert result.error is None
    assert session.diagnosis is not None


# --- Prerequisites --------------------------------------------------------


def test_recommend_is_not_permitted_before_a_comparison_exists(session):
    assert AdvisoryAction.RECOMMEND not in permitted_actions(session)


def test_clarification_is_not_permitted_while_questions_are_outstanding(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))

    permitted = permitted_actions(session)
    assert AdvisoryAction.ASK_CLARIFICATION not in permitted
    assert AdvisoryAction.COMPARE not in permitted


def test_revise_is_never_offered_in_this_iteration(session):
    """Its validation exists; its user flow does not, so it is not advertised."""
    assert AdvisoryAction.REVISE not in permitted_actions(session)


def test_a_thin_brief_only_permits_asking_for_context():
    from app.models import ManagerBrief

    empty = ManagerBrief(
        context_id="CTX-EMPTY", organisation="Fictional Co", situation=None
    )
    session = SessionStore().create(empty)

    permitted = permitted_actions(session)
    assert AdvisoryAction.REQUEST_CONTEXT in permitted
    assert AdvisoryAction.COMPARE not in permitted
    assert AdvisoryAction.RECOMMEND not in permitted


# --- Configuration --------------------------------------------------------


def test_building_a_client_without_credentials_raises_clearly(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "model_provider", None)
    from app.core.model_client import build_client

    with pytest.raises(ModelNotConfigured, match="MODEL_PROVIDER"):
        build_client()


def test_an_unimplemented_provider_is_refused_rather_than_substituted(monkeypatch):
    from app.config import settings
    from app.core.model_client import build_client

    monkeypatch.setattr(settings, "model_provider", "anthropic")
    monkeypatch.setattr(settings, "model_api_key", "test-key")

    with pytest.raises(ModelNotConfigured, match="only 'openai' is implemented"):
        build_client()


def test_sdk_exception_types_used_by_the_adapter_exist():
    """Pins the SDK surface the adapter depends on.

    If a future SDK renames one of these, the adapter would stop catching it and
    the failure would surface as an unhandled error rather than a clear message.
    """
    for name in (
        "AuthenticationError",
        "RateLimitError",
        "APITimeoutError",
        "APIConnectionError",
        "BadRequestError",
        "APIStatusError",
    ):
        assert hasattr(openai, name), f"openai.{name} is missing"
