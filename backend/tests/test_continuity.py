"""Regressions for what the first live run exposed.

The live run of 2026-09-18 surfaced four behaviours worth pinning:

1. A turn that timed out reported "Nothing partial was saved" while a validated
   comparison had in fact been saved and kept.
2. Continue would re-run a comparison that was still current, paying twice for
   the same analysis.
3. The advisor diagnosed the brief *after* comparing it, which is a reading of
   the brief that arrives too late to inform anything.
4. The model cited skipped question identifiers as sources, which the validation
   boundary rejected twice at a cost of roughly a quarter of the session.
"""

from __future__ import annotations

import asyncio

import pytest

from app.core import assemble
from app.core.advisory import AdvisoryEngine, permitted_actions
from app.core.limits import Limits
from app.data import load_sample_brief
from app.models import AdvisoryAction
from app.store.session import SessionStore
from tests import doubles


def run(coro):
    return asyncio.run(coro)


@pytest.fixture()
def session():
    return SessionStore().create(load_sample_brief())


# --- 1. A timeout keeps what was already validated ------------------------


def test_a_timeout_keeps_the_comparison_and_says_so(session):
    """The exact shape of the live failure.

    Compare completes and is committed. The next step overruns the deadline.
    The comparison must survive, and the message must say it survived.
    """
    limits = Limits(max_turn_seconds=1.2, max_model_requests=10)
    client = doubles.ScriptedClient(
        [
            doubles.next_action("compare"),
            doubles.comparison(),
            doubles.next_action("recommend"),
            doubles.Delayed(doubles.recommendation(), seconds=5.0),
        ]
    )

    result = run(AdvisoryEngine(client, limits=limits).run_turn(session))

    assert result.error["limit"] == "max_turn_seconds"

    # The comparison was validated before the deadline. It stays.
    assert session.comparison is not None
    # The interrupted step produced nothing.
    assert session.recommendation is None

    message = result.error["message"]
    assert "Completed and saved this turn: compare." in message
    assert "Interrupted before finishing: recommend." in message
    assert "Still held from this session: comparison." in message
    assert "Nothing partial was saved" not in message

    assert result.error["completed_this_turn"] == ["compare"]
    assert result.error["interrupted"] == "recommend"


def test_a_timeout_with_nothing_committed_says_that_instead(session):
    limits = Limits(max_turn_seconds=0.8)
    client = doubles.ScriptedClient(
        [
            doubles.next_action("diagnose"),
            doubles.Delayed(doubles.diagnosis(), seconds=5.0),
        ]
    )

    result = run(AdvisoryEngine(client, limits=limits).run_turn(session))

    message = result.error["message"]
    assert "No step completed this turn, so nothing new was saved." in message
    assert "Interrupted before finishing: diagnose." in message
    assert result.error["completed_this_turn"] == []


# --- 2. Continue does not repeat a current comparison ---------------------


def test_continue_does_not_re_offer_a_comparison_that_is_still_current(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("compare"), doubles.comparison(), doubles.next_action("await_user")]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    assert session.comparison is not None
    assert session.comparison_is_current() is True

    permitted = permitted_actions(session)
    assert AdvisoryAction.COMPARE not in permitted
    assert AdvisoryAction.RECOMMEND in permitted


def test_continue_reaches_the_recommendation_from_a_saved_comparison(session):
    """The recovery path after a timeout: Continue picks up, it does not restart."""
    client = doubles.ScriptedClient(
        [doubles.next_action("compare"), doubles.comparison(), doubles.next_action("await_user")]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    comparison = session.comparison
    requests_so_far = len(client.calls)

    client.queue(doubles.next_action("recommend"), doubles.recommendation())
    result = run(engine.run_turn(session))

    assert result.actions == ["recommend"]
    assert session.recommendation is not None
    # The stored comparison is the same object; it was not regenerated.
    assert session.comparison is comparison
    # Two requests: one selector, one recommend. No second comparison.
    assert len(client.calls) - requests_so_far == 2


def test_new_answers_make_the_comparison_stale_again(session):
    """Re-comparing is right when the manager has said something since."""
    client = doubles.ScriptedClient(
        [
            doubles.next_action("ask_clarification"),
            doubles.clarification(),
        ]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA", "Q-TEAM"})

    client.queue(doubles.next_action("compare"), doubles.comparison(), doubles.next_action("await_user"))
    run(engine.run_turn(session))
    assert session.comparison_is_current() is True
    assert AdvisoryAction.COMPARE not in permitted_actions(session)

    # The manager supplies more. The comparison no longer reflects what is known.
    session.record_answers({"Q-TEAM": "The operations director would own it."}, skipped=set())
    assert session.comparison_is_current() is False
    assert AdvisoryAction.COMPARE in permitted_actions(session)


# --- 3. Diagnosis comes before the comparison, or not at all -------------


def test_diagnose_is_offered_before_a_comparison_exists(session):
    assert AdvisoryAction.DIAGNOSE in permitted_actions(session)


def test_diagnose_is_not_offered_once_a_comparison_exists(session):
    """The live run diagnosed after comparing. That is now unavailable."""
    client = doubles.ScriptedClient(
        [doubles.next_action("compare"), doubles.comparison(), doubles.next_action("await_user")]
    )
    run(AdvisoryEngine(client).run_turn(session))

    assert session.diagnosis is None
    assert AdvisoryAction.DIAGNOSE not in permitted_actions(session)


def test_diagnosis_remains_optional(session):
    """Nothing forces it. A session can reach a recommendation without one."""
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


# --- 4. One clarification round by default -------------------------------


def test_only_one_clarification_round_is_offered_by_default(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"})

    permitted = permitted_actions(session)
    assert AdvisoryAction.ASK_CLARIFICATION not in permitted
    assert AdvisoryAction.COMPARE in permitted


def test_the_round_limit_is_configurable(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    limits = Limits(max_clarification_rounds=2)
    run(AdvisoryEngine(client, limits=limits).run_turn(session))

    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped=set())

    assert AdvisoryAction.ASK_CLARIFICATION in permitted_actions(session, limits)
    assert AdvisoryAction.ASK_CLARIFICATION not in permitted_actions(session, Limits())


# --- 5. Skipped questions are not citable, and the model is told so ------


def test_citable_answers_excludes_skipped_and_unanswered(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))

    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"})

    citable = session.citable_answers()
    assert [entry["id"] for entry in citable] == ["Q-VOLUME"]
    assert citable[0]["answer"] == "About 400 a week."


def test_the_prompt_separates_citable_answers_from_question_status(session):
    """The mitigation for the live rejections, checked on the text actually sent."""
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))
    session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"})

    text = assemble.action_input(session, AdvisoryAction.COMPARE)

    assert "# Answers you may cite" in text
    assert "# Status of every question asked" in text

    citable_section = text.split("# Answers you may cite")[1].split(
        "# Status of every question asked"
    )[0]
    assert "Q-VOLUME" in citable_section
    assert "Q-DATA" not in citable_section, "a skipped question appeared in the citable list"

    assert "never as a source" in text


def test_with_no_answers_the_citable_section_says_so_plainly(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))
    session.record_answers({}, skipped={"Q-VOLUME", "Q-DATA", "Q-TEAM"})

    text = assemble.action_input(session, AdvisoryAction.COMPARE)
    assert "no claim may cite one" in text


# --- 6. The selector sees substance, not flags ---------------------------


def test_the_selector_receives_the_findings_not_just_booleans(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("compare"), doubles.comparison(), doubles.next_action("await_user")]
    )
    run(AdvisoryEngine(client).run_turn(session))

    text = assemble.selector_input(session, {AdvisoryAction.RECOMMEND})

    assert "# What you have already concluded" in text
    # The criteria and the recorded unknowns, not merely has_comparison: true.
    assert "criteria_considered" in text
    assert "unknowns_per_initiative" in text
    assert "still_current" in text
    assert "steps_completed" in text


def test_the_selector_summary_is_empty_before_anything_happens(session):
    text = assemble.selector_input(session, {AdvisoryAction.DIAGNOSE})
    assert "Nothing yet." in text


# --- 7. Usage accounting -------------------------------------------------


def test_usage_reports_reasoning_and_cached_tokens_without_double_counting():
    from app.core.model_client import ModelCall

    call = ModelCall(
        parsed=doubles.next_action("compare"),
        model="gpt-5-mini",
        input_tokens=2000,
        output_tokens=1500,
        total_tokens=3500,
        reasoning_tokens=900,
        cached_input_tokens=1200,
        reasoning_effort="low",
        duration_ms=1234,
        response_id="resp_x",
    )
    usage = call.usage()

    assert usage["reasoning_tokens"] == 900
    assert usage["cached_input_tokens"] == 1200
    # The totals are the provider's own and are not adjusted.
    assert usage["output_tokens"] == 1500
    assert usage["total_tokens"] == 3500
    assert "included in output_tokens" in usage["token_accounting"]


def test_missing_usage_details_stay_none_rather_than_zero():
    """A figure the provider did not send is not a measured zero."""
    from app.core.model_client import ModelCall

    call = ModelCall(
        parsed=doubles.next_action("compare"),
        model="gpt-5-mini",
        input_tokens=100,
        output_tokens=200,
        total_tokens=300,
        duration_ms=1,
        response_id=None,
    )
    usage = call.usage()
    assert usage["reasoning_tokens"] is None
    assert usage["cached_input_tokens"] is None
