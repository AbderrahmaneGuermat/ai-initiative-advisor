"""HTTP surface, exercised end to end with a deterministic double.

Uses httpx against the ASGI app in process, so there is no server, no network
and no API key anywhere in this file.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest

from app.core.model_client import ModelNotConfigured, ModelRateLimited
from app.main import app
from tests import doubles


def call(coro):
    return asyncio.run(coro)


async def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    )


@pytest.fixture(autouse=True)
def fresh_store(monkeypatch):
    """A clean in-memory store per test."""
    from app.store.session import SessionStore

    store = SessionStore()
    monkeypatch.setattr("app.api.routes.store", store)
    return store


@pytest.fixture()
def scripted(monkeypatch):
    """Route every engine the API builds to one scripted double."""
    client = doubles.ScriptedClient()
    monkeypatch.setattr("app.api.routes.build_client", lambda: client)
    return client


# --- Health, diagnostics, scenario ---------------------------------------


def test_health_reports_the_stage_and_never_returns_a_key():
    async def run():
        async with await _client() as http:
            response = await http.get("/api/health")
            assert response.status_code == 200
            body = response.json()
            assert body["status"] == "ok"
            assert isinstance(body["model_configured"], bool)
            assert "key" not in str(body).lower().replace("model_configured", "")
            assert "revision user flow" in body["not_implemented"]

    call(run())


def test_diagnostics_exposes_prompt_hashes_but_no_secret():
    async def run():
        async with await _client() as http:
            body = (await http.get("/api/diagnostics")).json()
            assert body["session_persistence"] == "in-memory only; lost on restart"
            assert "revise" in body["unavailable_actions"]
            assert body["prompts"], "prompt list should not be empty"
            assert all("content_hash" in entry for entry in body["prompts"])
            # The key must never appear, under any field name.
            assert "sk-" not in str(body)

    call(run())


def test_scenario_is_served_and_labelled_as_fiction():
    async def run():
        async with await _client() as http:
            body = (await http.get("/api/scenario")).json()
            assert body["brief"]["organisation"] == "Larkfield Regional Freight"
            assert "fictional" in body["label"].lower()
            assert len(body["brief"]["initiatives"]) == 3

    call(run())


# --- The manager's flow ---------------------------------------------------


def _brief() -> dict:
    from app.data import load_sample_brief

    return load_sample_brief().model_dump(mode="json")


def test_session_flow_from_start_to_recommendation(scripted):
    scripted.queue(
        doubles.next_action("diagnose"),
        doubles.diagnosis(),
        doubles.next_action("ask_clarification"),
        doubles.clarification(),
    )

    async def run():
        async with await _client() as http:
            start = await http.post("/api/sessions", json={"brief": _brief()})
            assert start.status_code == 200
            body = start.json()
            session_id = body["session_id"]

            assert body["diagnosis"] is not None
            assert len(body["questions"]) == 3
            assert body["awaiting_answers"] is True
            assert body["recommendation"] is None

            scripted.queue(
                doubles.next_action("compare"),
                doubles.comparison(),
                doubles.next_action("recommend"),
                doubles.recommendation(),
            )

            answered = await http.post(
                f"/api/sessions/{session_id}/answers",
                json={"answers": {"Q-VOLUME": "About 400 a week."}, "skipped": ["Q-DATA"]},
            )
            assert answered.status_code == 200
            body = answered.json()

            assert body["comparison"] is not None
            assert body["recommendation"] is not None
            assert body["error"] is None

            statuses = {q["id"]: q["status"] for q in body["questions"]}
            assert statuses["Q-VOLUME"] == "answered"
            assert statuses["Q-DATA"] == "skipped"
            assert statuses["Q-TEAM"] == "unanswered"

            # Open questions come from session state, not from the advice text.
            open_ids = {q["id"] for q in body["open_questions"]}
            assert open_ids == {"Q-DATA", "Q-TEAM"}

    call(run())


def test_trace_endpoint_reports_prompt_versions_and_usage(scripted):
    scripted.queue(
        doubles.next_action("diagnose"), doubles.diagnosis(), doubles.next_action("await_user")
    )

    async def run():
        async with await _client() as http:
            session_id = (
                await http.post("/api/sessions", json={"brief": _brief()})
            ).json()["session_id"]

            trace = (await http.get(f"/api/sessions/{session_id}/trace")).json()
            assert trace["last_budget"]["model_requests"] == 3
            assert trace["records"][0]["prompt"]["prompt_id"] == "action.diagnose"
            assert trace["records"][0]["usage"]["total_tokens"] == 300

    call(run())


def test_answers_for_an_unknown_question_are_refused(scripted):
    scripted.queue(doubles.next_action("ask_clarification"), doubles.clarification())

    async def run():
        async with await _client() as http:
            session_id = (
                await http.post("/api/sessions", json={"brief": _brief()})
            ).json()["session_id"]

            response = await http.post(
                f"/api/sessions/{session_id}/answers",
                json={"answers": {"Q-NOT-ASKED": "Something."}, "skipped": []},
            )
            assert response.status_code == 400
            assert "no such question" in response.json()["detail"]["message"]

    call(run())


def test_unknown_session_returns_404(scripted):
    async def run():
        async with await _client() as http:
            response = await http.get("/api/sessions/doesnotexist")
            assert response.status_code == 404
            assert "restart" in response.json()["detail"]["message"]

    call(run())


def test_an_invalid_brief_is_rejected_before_a_session_exists(scripted):
    async def run():
        async with await _client() as http:
            response = await http.post(
                "/api/sessions",
                json={"brief": {"context_id": "not-a-context-id", "organisation": "X"}},
            )
            assert response.status_code == 422

    call(run())


# --- Failures the manager sees -------------------------------------------


def test_missing_credentials_return_503_with_an_actionable_message(monkeypatch):
    def unconfigured():
        raise ModelNotConfigured(
            "MODEL_API_KEY is not set. Configure it in a local .env file."
        )

    monkeypatch.setattr("app.api.routes.build_client", unconfigured)

    async def run():
        async with await _client() as http:
            response = await http.post("/api/sessions", json={"brief": _brief()})
            assert response.status_code == 503
            detail = response.json()["detail"]
            assert detail["kind"] == "ModelNotConfigured"
            assert "MODEL_API_KEY" in detail["message"]
            assert detail["recoverable"] is False

    call(run())


def test_the_app_starts_and_serves_health_without_any_credentials(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "model_api_key", None)
    monkeypatch.setattr(settings, "model_provider", None)

    async def run():
        async with await _client() as http:
            assert (await http.get("/api/health")).status_code == 200
            assert (await http.get("/api/scenario")).status_code == 200

    call(run())


def test_a_provider_failure_is_reported_and_no_advice_is_invented(scripted):
    scripted.queue(doubles.next_action("diagnose"), ModelRateLimited("429 from provider"))

    async def run():
        async with await _client() as http:
            body = (await http.post("/api/sessions", json={"brief": _brief()})).json()

            assert body["error"]["kind"] == "ModelRateLimited"
            assert body["error"]["recoverable"] is True
            assert body["diagnosis"] is None
            assert body["comparison"] is None
            assert body["recommendation"] is None

    call(run())


def test_rejected_output_is_reported_without_reaching_the_manager_as_advice(scripted):
    scripted.queue(
        doubles.next_action("compare"),
        doubles.comparison(context_id="CTX-WRONG"),
        doubles.comparison(context_id="CTX-STILL-WRONG"),
    )

    async def run():
        async with await _client() as http:
            body = (await http.post("/api/sessions", json={"brief": _brief()})).json()

            assert body["error"]["kind"] == "invalid_output"
            assert body["comparison"] is None

    call(run())


def test_editing_the_brief_starts_a_new_session(scripted):
    """Two sessions, two identifiers. No pretence of a revision."""
    scripted.queue(doubles.next_action("await_user"), doubles.next_action("await_user"))

    async def run():
        async with await _client() as http:
            first = (await http.post("/api/sessions", json={"brief": _brief()})).json()

            edited = _brief()
            edited["constraints"][0]["value"] = "60,000 EUR after a freeze"
            second = (await http.post("/api/sessions", json={"brief": edited})).json()

            assert first["session_id"] != second["session_id"]
            assert second["recommendation"] is None

    call(run())
