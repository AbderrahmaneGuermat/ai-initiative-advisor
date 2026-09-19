"""State consistency: advice must not rest on analysis the answers have overtaken.

The problem these cover: a manager answers a question, which makes the stored
comparison out of date, and the advisor recommends from it anyway. The result
would contradict the very answer that was just given, with nothing to show that
had happened.

Six behaviours are pinned here:

1. A genuinely new answer makes the comparison outdated.
2. A recommendation cannot be accepted until that comparison is refreshed.
3. Continue reuses a current comparison rather than repeating it.
4. An identical resubmission invalidates nothing and recomputes nothing.
5. A failed refresh keeps the history and does not present outdated advice as
   current.
6. One answer, one skip and one blank completes the round with all three
   statuses retained.
"""

from __future__ import annotations

import asyncio

import pytest

from app.core.advisory import AdvisoryEngine, permitted_actions, validation_context
from app.core.validation import OutputRejected, validate_output
from app.data import load_sample_brief
from app.models import AdvisoryAction, AnswerStatus
from app.store.session import SessionStore
from tests import doubles


def run(coro):
    return asyncio.run(coro)


@pytest.fixture()
def session():
    return SessionStore().create(load_sample_brief())


def _reach_recommendation(session) -> doubles.ScriptedClient:
    """Ask, answer, compare, recommend. Leaves a current recommendation."""
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    client.queue(
        doubles.next_action("compare"),
        doubles.comparison(),
        doubles.next_action("recommend"),
        doubles.recommendation(),
    )
    run(
        engine.run_turn(
            session,
            prepare=lambda: session.record_answers(
                {"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"}
            ),
        )
    )
    assert session.recommendation is not None
    return client


# --- 1. A new answer makes the comparison outdated ------------------------


def test_a_new_answer_makes_the_comparison_outdated(session):
    client = _reach_recommendation(session)
    assert session.comparison_is_current() is True
    assert session.recommendation_is_current() is True

    version_before = session.answers_version
    session.record_answers({"Q-TEAM": "The operations director would own it."}, skipped=set())

    assert session.answers_version == version_before + 1
    assert session.comparison_is_current() is False
    assert session.recommendation_is_current() is False
    assert client is not None


def test_status_reporting_names_outdated_results(session):
    _reach_recommendation(session)
    session.record_answers({"Q-TEAM": "The operations director."}, skipped=set())

    assert session.result_status(AdvisoryAction.COMPARE) == "outdated"
    assert session.result_status(AdvisoryAction.RECOMMEND) == "outdated"


# --- 2. No recommendation on an outdated comparison ----------------------


def test_recommend_is_not_offered_while_the_comparison_is_outdated(session):
    _reach_recommendation(session)
    session.record_answers({"Q-TEAM": "The operations director."}, skipped=set())

    permitted = permitted_actions(session)
    assert AdvisoryAction.RECOMMEND not in permitted
    assert AdvisoryAction.COMPARE in permitted, "the refresh must be available"


def test_validation_refuses_a_recommendation_built_on_an_outdated_comparison(session):
    _reach_recommendation(session)
    session.record_answers({"Q-TEAM": "The operations director."}, skipped=set())

    context = validation_context(session)
    assert context.comparison_is_current is False

    with pytest.raises(OutputRejected) as caught:
        validate_output(AdvisoryAction.RECOMMEND, doubles.recommendation(), context)

    assert any("predates" in error for error in caught.value.errors)


def test_the_commit_boundary_refuses_it_too(session):
    """A second, independent guard, so the rule does not depend on one caller."""
    from app.core.advisory import AdvisoryEngine as Engine
    from app.models import Recommendation

    _reach_recommendation(session)
    session.record_answers({"Q-TEAM": "The operations director."}, skipped=set())

    payload = Recommendation.model_validate(doubles.recommendation().model_dump())

    with pytest.raises(OutputRejected, match="predates"):
        Engine._commit(
            session=session,
            action=AdvisoryAction.RECOMMEND,
            payload=payload,
            turn=session.turn,
            prompt_trace={},
            usage={},
            repair_usage=None,
            repaired=False,
        )


def test_refreshing_the_comparison_makes_recommending_available_again(session):
    client = _reach_recommendation(session)
    session.record_answers({"Q-TEAM": "The operations director."}, skipped=set())

    client.queue(doubles.next_action("compare"), doubles.comparison(), doubles.next_action("await_user"))
    run(AdvisoryEngine(client).run_turn(session))

    assert session.comparison_is_current() is True
    assert session.recommendation_is_current() is False
    assert AdvisoryAction.RECOMMEND in permitted_actions(session)


def test_diagnosis_stays_optional_under_the_new_prerequisite(session):
    """The rule is about data consistency, not a mandatory sequence."""
    client = doubles.ScriptedClient(
        [
            doubles.next_action("compare"),
            doubles.comparison(),
            doubles.next_action("recommend"),
            doubles.recommendation(),
        ]
    )
    result = run(AdvisoryEngine(client).run_turn(session))

    assert result.error is None
    assert session.diagnosis is None
    assert session.recommendation is not None


# --- 3. Continue reuses a current comparison -----------------------------


def test_continue_reuses_a_current_comparison_without_repeating_it(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("compare"), doubles.comparison(), doubles.next_action("await_user")]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    comparison = session.comparison
    calls_before = len(client.calls)

    client.queue(doubles.next_action("recommend"), doubles.recommendation())
    result = run(engine.run_turn(session))

    assert result.actions == ["recommend"]
    assert session.comparison is comparison
    assert len(client.calls) - calls_before == 2, "one selector call and one recommend call"


# --- 4. An identical resubmission changes nothing ------------------------


def test_an_identical_resubmission_does_not_invalidate_current_results(session):
    _reach_recommendation(session)
    version = session.answers_version

    changed = session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"})

    assert changed is False
    assert session.answers_version == version
    assert session.comparison_is_current() is True
    assert session.recommendation_is_current() is True


def test_surrounding_whitespace_is_not_a_new_answer(session):
    _reach_recommendation(session)
    version = session.answers_version

    changed = session.record_answers({"Q-VOLUME": "  About 400 a week.  "}, skipped={"Q-DATA"})

    assert changed is False
    assert session.answers_version == version


def test_an_identical_resubmission_triggers_no_model_request(session):
    """Nothing to decide, so nothing is asked. Not even the selector."""
    client = _reach_recommendation(session)
    calls_before = len(client.calls)

    result = run(
        AdvisoryEngine(client).run_turn(
            session,
            prepare=lambda: session.record_answers(
                {"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"}
            ),
        )
    )

    assert len(client.calls) == calls_before, "a no-op resubmission made a provider request"
    assert result.awaiting_user is True
    assert result.budget["model_requests"] == 0
    assert session.recommendation_is_current() is True


def test_a_genuinely_different_answer_does_advance_the_version(session):
    _reach_recommendation(session)
    version = session.answers_version

    changed = session.record_answers({"Q-VOLUME": "Closer to 900 a week."}, skipped=set())

    assert changed is True
    assert session.answers_version == version + 1


def test_changing_a_status_alone_counts_as_a_change(session):
    """Answering a question that was skipped is new information."""
    _reach_recommendation(session)
    version = session.answers_version

    changed = session.record_answers({"Q-DATA": "Three years of history exists."}, skipped=set())

    assert changed is True
    assert session.answers_version == version + 1
    statuses = {qid: status for qid, _q, _w, status in session.all_questions()}
    assert statuses["Q-DATA"] is AnswerStatus.ANSWERED


# --- 5. A failed refresh preserves history -------------------------------


def test_a_failed_refresh_keeps_history_and_does_not_present_stale_advice(session):
    from app.core.model_client import ModelRateLimited

    client = _reach_recommendation(session)
    old_recommendation = session.recommendation
    old_comparison = session.comparison
    records_before = len(session.records)

    client.queue(doubles.next_action("compare"), ModelRateLimited("429"))
    result = run(
        AdvisoryEngine(client).run_turn(
            session,
            prepare=lambda: session.record_answers(
                {"Q-TEAM": "The operations director."}, skipped=set()
            ),
        )
    )

    assert result.error["kind"] == "ModelRateLimited"

    # History is intact. Nothing validated was removed.
    assert len(session.records) == records_before
    assert session.comparison is old_comparison
    assert session.recommendation is old_recommendation

    # But neither is presented as current.
    assert session.comparison_is_current() is False
    assert session.recommendation_is_current() is False
    assert session.result_status(AdvisoryAction.RECOMMEND) == "outdated"

    # And the refresh is still available.
    assert AdvisoryAction.COMPARE in permitted_actions(session)


def test_a_timed_out_refresh_behaves_the_same(session):
    from app.core.limits import Limits

    client = _reach_recommendation(session)
    old_recommendation = session.recommendation

    client.queue(
        doubles.next_action("compare"),
        doubles.Delayed(doubles.comparison(), seconds=5.0),
    )
    result = run(
        AdvisoryEngine(client, limits=Limits(max_turn_seconds=1.0)).run_turn(
            session,
            prepare=lambda: session.record_answers(
                {"Q-TEAM": "The operations director."}, skipped=set()
            ),
        )
    )

    assert result.error["limit"] == "max_turn_seconds"
    assert session.recommendation is old_recommendation
    assert session.recommendation_is_current() is False
    assert "Still held from this session" in result.error["message"]


# --- 6. One answer, one skip, one blank ----------------------------------


def test_one_answer_one_skip_one_blank_completes_the_round(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))

    assert session.round_is_pending(0) is True
    assert session.has_pending_questions() is True

    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"})

    # The round is complete: nothing further is being asked of the manager.
    assert session.round_is_pending(0) is False
    assert session.has_pending_questions() is False

    # All three statuses survive, distinct from one another.
    statuses = {qid: status for qid, _q, _w, status in session.all_questions()}
    assert statuses["Q-VOLUME"] is AnswerStatus.ANSWERED
    assert statuses["Q-DATA"] is AnswerStatus.SKIPPED
    assert statuses["Q-TEAM"] is AnswerStatus.UNANSWERED

    # The untouched one is an open unknown, not an outstanding request.
    open_ids = {qid for qid, _q, _w, _s in session.open_questions()}
    assert open_ids == {"Q-DATA", "Q-TEAM"}


def test_the_view_separates_answer_status_from_awaiting_a_reply(session):
    """The distinction the interface needs, checked on what the API returns."""
    from app.api.routes import _question_view

    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))

    before = {q["id"]: q for q in _question_view(session)}
    assert all(q["awaiting_response"] is True for q in before.values())

    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"})

    after = {q["id"]: q for q in _question_view(session)}
    assert all(q["awaiting_response"] is False for q in after.values())

    # Status still distinguishes the three outcomes.
    assert after["Q-VOLUME"]["status"] == "answered"
    assert after["Q-DATA"]["status"] == "skipped"
    assert after["Q-TEAM"]["status"] == "unanswered"


# --- The HTTP surface says the same thing ---------------------------------


def test_the_api_does_not_serve_an_outdated_recommendation_as_current(monkeypatch):
    """End to end through the API, since this is what the interface reads."""
    import httpx

    from app.main import app
    from app.store.session import SessionStore

    store = SessionStore()
    monkeypatch.setattr("app.api.routes.store", store)

    client = doubles.ScriptedClient()
    monkeypatch.setattr("app.api.routes.build_client", lambda: client)

    brief = load_sample_brief().model_dump(mode="json")

    async def scenario():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as http:
            client.queue(doubles.next_action("ask_clarification"), doubles.clarification())
            body = (await http.post("/api/sessions", json={"brief": brief})).json()
            sid = body["session_id"]
            assert all(q["awaiting_response"] is True for q in body["questions"])

            client.queue(
                doubles.next_action("compare"),
                doubles.comparison(),
                doubles.next_action("recommend"),
                doubles.recommendation(),
            )
            body = (
                await http.post(
                    f"/api/sessions/{sid}/answers",
                    json={"answers": {"Q-VOLUME": "About 400 a week."}, "skipped": ["Q-DATA"]},
                )
            ).json()

            assert body["recommendation"] is not None
            assert body["previous_recommendation"] is None
            assert body["recommendation_status"] == "current"
            assert body["comparison_status"] == "current"
            assert all(q["awaiting_response"] is False for q in body["questions"])

            # A new answer, and the refresh fails.
            from app.core.model_client import ModelRateLimited

            client.queue(doubles.next_action("compare"), ModelRateLimited("429"))
            body = (
                await http.post(
                    f"/api/sessions/{sid}/answers",
                    json={"answers": {"Q-TEAM": "The operations director."}, "skipped": []},
                )
            ).json()

            assert body["error"]["kind"] == "ModelRateLimited"
            # Not served as current advice.
            assert body["recommendation"] is None
            # But kept, labelled, and available to read.
            assert body["previous_recommendation"] is not None
            assert body["recommendation_status"] == "outdated"
            assert body["comparison_status"] == "outdated"
            # History is intact.
            actions = [entry["action"] for entry in body["history"]]
            assert actions.count("compare") == 1
            assert actions.count("recommend") == 1

    asyncio.run(scenario())
