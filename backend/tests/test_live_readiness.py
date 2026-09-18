"""Regressions for the findings raised against commit a19dce9.

Four defects, four groups of tests:

1. Placeholder configuration read as configured.
2. The turn deadline was checked between iterations, so an in-flight request
   could overrun it and still commit.
3. The execution trace was not persisted: selector calls, repairs and failures
   left no record.
4. Answers were written outside the session lock, so they could change while a
   turn was awaiting a model response.
"""

from __future__ import annotations

import asyncio

import pytest

from app.core.advisory import AdvisoryEngine
from app.core.configuration import check_configuration
from app.core.limits import Limits
from app.core.model_client import ModelNotConfigured, ModelRateLimited, build_client
from app.data import load_sample_brief
from app.models import AnswerStatus
from app.store.session import SessionStore
from tests import doubles


def run(coro):
    return asyncio.run(coro)


@pytest.fixture()
def session():
    return SessionStore().create(load_sample_brief())


@pytest.fixture()
def configured(monkeypatch):
    """Valid-looking local configuration."""
    from app.config import settings

    monkeypatch.setattr(settings, "model_provider", "openai")
    monkeypatch.setattr(settings, "model_name", "gpt-5-mini")
    monkeypatch.setattr(settings, "model_api_key", "sk-test-not-a-real-key-000")


# --- 1. Configuration status ---------------------------------------------


def test_the_committed_placeholder_does_not_count_as_configured(monkeypatch):
    """The exact value in .env.example.

    Copying the example and forgetting to edit it is the most likely setup
    mistake there is, and it previously reported the advisor as ready.
    """
    from app.config import settings

    monkeypatch.setattr(settings, "model_provider", "openai")
    monkeypatch.setattr(settings, "model_api_key", "your-openai-api-key-here")

    status = check_configuration()
    assert status.configured_locally is False
    assert any("placeholder" in problem for problem in status.problems)


@pytest.mark.parametrize(
    "key",
    ["", "   ", "changeme", "TODO", "  Placeholder  ", "<your key>", "your-api-key-here"],
)
def test_obvious_non_keys_are_rejected(monkeypatch, key):
    from app.config import settings

    monkeypatch.setattr(settings, "model_provider", "openai")
    monkeypatch.setattr(settings, "model_api_key", key)

    assert check_configuration().configured_locally is False


def test_an_unusual_but_plausible_key_is_accepted(monkeypatch):
    """No brittle format rule.

    Provider key formats change. A check that rejects a valid key is worse than
    one that lets an invalid key reach the provider, where it fails clearly.
    """
    from app.config import settings

    monkeypatch.setattr(settings, "model_provider", "openai")
    monkeypatch.setattr(settings, "model_api_key", "totally-unexpected-format-9f3b2a")

    status = check_configuration()
    assert status.configured_locally is True
    assert status.problems == []


def test_an_unsupported_provider_is_rejected(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "model_provider", "anthropic")
    monkeypatch.setattr(settings, "model_api_key", "sk-test-000")

    status = check_configuration()
    assert status.configured_locally is False
    assert any("no adapter" in problem for problem in status.problems)


def test_the_health_check_and_the_client_agree(monkeypatch):
    """One implementation, so a green status and a refused session cannot coexist."""
    from app.config import settings

    monkeypatch.setattr(settings, "model_provider", "openai")
    monkeypatch.setattr(settings, "model_api_key", "your-openai-api-key-here")

    assert check_configuration().configured_locally is False
    with pytest.raises(ModelNotConfigured):
        build_client()


def test_configuration_status_does_not_claim_authentication(monkeypatch, configured):
    """It reports presence. Only a real request establishes that a key works.

    The field is named ``configured_locally`` rather than ``connected`` or
    ``authenticated``, and the note says plainly what it does not cover. A
    manager who sees "connected" and then hits an authentication error on their
    first session has been misled by the status indicator.
    """
    status = check_configuration()
    assert status.configured_locally is True
    assert status.problems == []
    assert "does not mean the credentials are valid" in status.note
    assert "only a completed request" in status.note


# --- 2. The turn deadline -------------------------------------------------


def test_a_request_that_overruns_the_deadline_is_cancelled(session):
    """The core regression.

    Previously the elapsed check ran only between iterations, so a single slow
    call could run far past the limit and commit its result. Now the deadline
    bounds the awaited call itself.
    """
    limits = Limits(max_turn_seconds=0.25, max_model_requests=10)
    client = doubles.ScriptedClient(
        [
            doubles.next_action("diagnose"),
            doubles.Delayed(doubles.diagnosis(), seconds=5.0),
        ]
    )

    result = run(AdvisoryEngine(client, limits=limits).run_turn(session))

    assert result.error is not None
    assert result.error["kind"] == "limit"
    assert result.error["limit"] == "max_turn_seconds"

    # Nothing was committed, and the session is usable again.
    assert session.diagnosis is None
    assert session.records == []
    assert session.status == "ready"
    assert not session.lock.locked()


def test_the_overrun_completes_quickly_rather_than_waiting_for_the_slow_call(session):
    """Cancelled, not merely noticed afterwards.

    If the call were awaited to completion and only then rejected, this would
    take five seconds.
    """
    limits = Limits(max_turn_seconds=0.25)
    client = doubles.ScriptedClient(
        [
            doubles.next_action("diagnose"),
            doubles.Delayed(doubles.diagnosis(), seconds=5.0),
        ]
    )

    async def timed():
        loop = asyncio.get_running_loop()
        started = loop.time()
        await AdvisoryEngine(client, limits=limits).run_turn(session)
        return loop.time() - started

    elapsed = run(timed())
    assert elapsed < 2.0, f"the overdue call was not cancelled promptly ({elapsed:.1f}s)"


def test_a_cancelled_request_is_recorded_without_invented_usage(session):
    limits = Limits(max_turn_seconds=0.25)
    client = doubles.ScriptedClient(
        [
            doubles.next_action("diagnose"),
            doubles.Delayed(doubles.diagnosis(), seconds=5.0),
        ]
    )
    run(AdvisoryEngine(client, limits=limits).run_turn(session))

    cancelled = [a for a in session.attempts if a.outcome == "cancelled"]
    assert len(cancelled) == 1
    assert cancelled[0].usage is None
    assert cancelled[0].usage_available is False


def test_the_session_is_usable_after_a_deadline_overrun(session):
    limits = Limits(max_turn_seconds=0.25)
    slow = doubles.ScriptedClient(
        [doubles.next_action("diagnose"), doubles.Delayed(doubles.diagnosis(), seconds=5.0)]
    )
    run(AdvisoryEngine(slow, limits=limits).run_turn(session))

    fast = doubles.ScriptedClient(
        [doubles.next_action("diagnose"), doubles.diagnosis(), doubles.next_action("await_user")]
    )
    result = run(AdvisoryEngine(fast).run_turn(session))

    assert result.error is None
    assert session.diagnosis is not None


# --- 3. Trace completeness ------------------------------------------------


def test_selector_calls_are_recorded(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("diagnose"), doubles.diagnosis(), doubles.next_action("await_user")]
    )
    run(AdvisoryEngine(client).run_turn(session))

    selectors = [a for a in session.attempts if a.kind == "selector"]
    assert len(selectors) == 2
    assert all(a.usage_available for a in selectors)
    assert all(a.prompt_trace["prompt_id"] == "action.next" for a in selectors)
    assert all(a.usage["total_tokens"] == 300 for a in selectors)


def test_a_repair_records_both_attempts_with_their_own_usage(session):
    client = doubles.ScriptedClient(
        [
            doubles.next_action("compare"),
            doubles.comparison(context_id="CTX-WRONG"),
            doubles.comparison(),
            doubles.next_action("await_user"),
        ]
    )
    run(AdvisoryEngine(client).run_turn(session))

    rejected = [a for a in session.attempts if a.outcome == "rejected"]
    repairs = [a for a in session.attempts if a.kind == "repair"]

    assert len(rejected) == 1
    assert rejected[0].kind == "action"
    assert rejected[0].usage_available is True

    assert len(repairs) == 1
    assert repairs[0].outcome == "accepted"
    assert repairs[0].prompt_trace["prompt_id"] == "support.repair"
    assert repairs[0].prompt_trace["repairing"] == "action.compare"

    # The accepted record keeps the repair cost separately rather than folding
    # it into the action's own usage.
    record = next(r for r in session.records if r.action.value == "compare")
    assert record.repaired is True
    assert record.repair_usage is not None
    assert record.usage is not None


def test_clarification_records_carry_provenance_and_usage(session):
    """Previously recorded with an empty prompt trace and no usage."""
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    run(AdvisoryEngine(client).run_turn(session))

    record = next(r for r in session.records if r.action.value == "ask_clarification")
    assert record.prompt_trace["prompt_id"] == "action.clarify"
    assert record.usage is not None
    assert record.usage["total_tokens"] == 300


def test_completed_attempts_survive_a_later_failure_in_the_same_turn(session):
    """The diagnosis succeeded; the compare call failed. Both are recorded."""
    client = doubles.ScriptedClient(
        [
            doubles.next_action("diagnose"),
            doubles.diagnosis(),
            doubles.next_action("compare"),
            ModelRateLimited("429"),
        ]
    )
    result = run(AdvisoryEngine(client).run_turn(session))

    assert result.error["kind"] == "ModelRateLimited"

    outcomes = [(a.kind, a.step, a.outcome) for a in session.attempts]
    assert ("selector", "select", "accepted") in outcomes
    assert ("action", "diagnose", "accepted") in outcomes
    assert ("action", "compare", "failed") in outcomes

    failed = next(a for a in session.attempts if a.outcome == "failed")
    assert failed.usage is None
    assert failed.usage_available is False
    assert "ModelRateLimited" in failed.detail[0]


def test_usage_is_never_invented_for_a_request_that_did_not_complete(session):
    client = doubles.ScriptedClient([doubles.next_action("diagnose"), ModelRateLimited("429")])
    run(AdvisoryEngine(client).run_turn(session))

    for attempt in session.attempts:
        if attempt.outcome in {"failed", "cancelled"} and attempt.usage is not None:
            # The one legitimate case: a call that completed but arrived late.
            assert "after the turn deadline" in " ".join(attempt.detail)
        if not attempt.usage_available:
            assert attempt.usage is None


def test_attempts_are_append_only_across_turns(session):
    client = doubles.ScriptedClient(
        [doubles.next_action("diagnose"), doubles.diagnosis(), doubles.next_action("await_user")]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))
    first = len(session.attempts)

    client.queue(doubles.next_action("await_user"))
    run(engine.run_turn(session))

    assert len(session.attempts) > first
    assert {a.turn for a in session.attempts} == {1, 2}


# --- 4. Answers and advisory execution do not overlap ---------------------


def test_answers_cannot_be_written_while_a_turn_is_awaiting_the_model(session):
    """The core regression for the locking finding.

    A turn is started that blocks inside its model call. While it is in flight,
    an answer submission is issued. The submission must wait: if it did not, the
    advice could be generated against one set of answers and committed against
    another.
    """
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))
    assert len(session.all_questions()) == 3

    observed: list[set[str]] = []

    def observe(_call_index: int) -> None:
        # What the answers looked like while a request was in flight.
        observed.append(session.answered_question_ids())

    async def scenario():
        client.on_call = observe
        client.queue(
            doubles.Delayed(doubles.next_action("compare"), seconds=0.30),
            doubles.comparison(),
            doubles.next_action("await_user"),
        )

        slow_turn = asyncio.create_task(engine.run_turn(session))
        await asyncio.sleep(0.05)  # let the turn reach its model call

        def record() -> None:
            session.record_answers({"Q-VOLUME": "About 400 a week."}, skipped={"Q-DATA"})

        answer_turn = asyncio.create_task(engine.run_turn(session, prepare=record))
        await asyncio.gather(slow_turn, answer_turn)

    client.queue(doubles.next_action("await_user"))
    run(scenario())

    # No request made during the first turn saw the answers, because the
    # submission could not run until the lock was free.
    assert observed, "the observation hook never ran"
    assert observed[0] == set(), "answers were applied while a turn was in flight"

    # Afterwards they are applied exactly once.
    statuses = {qid: status for qid, _q, _w, status in session.all_questions()}
    assert statuses["Q-VOLUME"] is AnswerStatus.ANSWERED
    assert statuses["Q-DATA"] is AnswerStatus.SKIPPED


def test_a_rejected_submission_leaves_the_session_unlocked_and_unchanged(session):
    """A bad submission is the caller's error, not a turn that half-ran."""
    client = doubles.ScriptedClient(
        [doubles.next_action("ask_clarification"), doubles.clarification()]
    )
    engine = AdvisoryEngine(client)
    run(engine.run_turn(session))

    turn_before = session.turn
    records_before = len(session.records)

    from app.store.session import SessionStateError

    def bad() -> None:
        session.record_answers({"Q-NEVER-ASKED": "Something."}, skipped=set())

    with pytest.raises(SessionStateError):
        run(engine.run_turn(session, prepare=bad))

    assert not session.lock.locked()
    assert session.turn == turn_before, "a refused submission must not consume a turn"
    assert len(session.records) == records_before


def test_two_turns_cannot_interleave(session):
    """The lock serialises turns, so their attempts do not interleave."""
    client = doubles.ScriptedClient()
    engine = AdvisoryEngine(client)

    async def scenario():
        client.queue(
            doubles.Delayed(doubles.next_action("diagnose"), seconds=0.20),
            doubles.diagnosis(),
            doubles.next_action("await_user"),
            doubles.next_action("await_user"),
        )
        await asyncio.gather(engine.run_turn(session), engine.run_turn(session))

    run(scenario())

    turns = [a.turn for a in session.attempts]
    # Every attempt from turn 1 precedes every attempt from turn 2.
    assert turns == sorted(turns), f"attempts interleaved across turns: {turns}"
