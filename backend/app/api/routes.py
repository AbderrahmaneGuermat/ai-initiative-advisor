"""HTTP surface.

Sessions are held in memory and are lost when the backend restarts. That is
stated in the endpoint descriptions as well as the README, so it is visible to
anyone reading the generated API documentation rather than only to whoever reads
the repository.

Provider details stay out of the manager's workflow. The advisory endpoints
return advice, questions and errors in the manager's terms. Model names, token
usage and prompt hashes are available, but only from the diagnostics endpoint.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.config import APP_VERSION, BUILD_STAGE, settings
from app.core.advisory import SUPPORTED_ACTIONS, AdvisoryEngine, permitted_actions
from app.core.configuration import check_configuration
from app.core.model_client import ModelError, ModelNotConfigured, build_client
from app.core.prompt_loader import PromptError, available_prompts, load_prompt
from app.data import load_sample_brief, sample_scenario_id
from app.models import AdvisoryAction, AnswerStatus, ManagerBrief
from app.store.session import SessionStateError, store

router = APIRouter()


# --- Health and diagnostics ----------------------------------------------


class HealthResponse(BaseModel):
    """Deliberately honest about how much of the application exists."""

    status: str
    service: str
    version: str
    stage: str
    model_configured_locally: bool = Field(
        description=(
            "Whether usable local configuration is present. NOT authentication: only a "
            "completed request to the provider establishes that the credentials work. "
            "The key itself is never returned."
        )
    )
    configuration_problems: list[str] = Field(
        description="What is missing or unusable about the local configuration, if anything"
    )
    configuration_note: str
    implemented: list[str]
    not_implemented: list[str]


@router.get("/health", response_model=HealthResponse, summary="Service health and build stage")
def health() -> HealthResponse:
    """Service health and local configuration presence.

    ``model_configured_locally`` says the settings look usable. It does not say
    the credentials work, because nothing short of a completed provider request
    establishes that.
    """
    configuration = check_configuration()
    return HealthResponse(
        status="ok",
        service="AI Initiative Advisor backend",
        version=APP_VERSION,
        stage=BUILD_STAGE,
        model_configured_locally=configuration.configured_locally,
        configuration_problems=configuration.problems,
        configuration_note=configuration.note,
        implemented=[
            "health",
            "data contracts",
            "runtime prompts loaded from disk",
            "OpenAI Responses API with structured outputs",
            "bounded advisory loop",
            "diagnosis, clarification, comparison, recommendation",
            "in-memory sessions",
        ],
        not_implemented=[
            "revision user flow",
            "persistence across restarts",
            "offline fixture replay",
            "export",
        ],
    )


@router.get("/diagnostics", summary="Developer metadata; not part of the manager's workflow")
def diagnostics() -> dict[str, Any]:
    """Technical detail kept out of the advisory endpoints.

    Reports whether a key is present, never its value.
    """
    try:
        prompts = [
            {
                "path": path,
                **{k: v for k, v in load_prompt(path).trace().items() if k != "prompt_path"},
            }
            for path in available_prompts()
        ]
        prompt_error = None
    except PromptError as exc:
        prompts = []
        prompt_error = str(exc)

    configuration = check_configuration()

    return {
        "stage": BUILD_STAGE,
        "version": APP_VERSION,
        "configuration": configuration.as_dict(),
        "provider": configuration.provider,
        "model": configuration.model,
        "max_output_tokens": settings.max_output_tokens,
        "model_timeout_seconds": settings.model_timeout_seconds,
        "supported_actions": sorted(a.value for a in SUPPORTED_ACTIONS),
        "unavailable_actions": sorted(
            a.value for a in AdvisoryAction if a not in SUPPORTED_ACTIONS
        ),
        "prompts": prompts,
        "prompt_error": prompt_error,
        "active_sessions": store.count(),
        "session_persistence": "in-memory only; lost on restart",
    }


# --- Scenario -------------------------------------------------------------


@router.get("/scenario", summary="The fictional sample brief")
def scenario() -> dict[str, Any]:
    """A hand-authored fictional brief, for loading into the editor.

    Not a recorded model response and not connected to any real organisation.
    """
    return {
        "scenario_id": sample_scenario_id(),
        "label": "Fictional sample scenario, written by hand",
        "brief": load_sample_brief().model_dump(mode="json"),
    }


# --- Sessions -------------------------------------------------------------


class StartSessionRequest(BaseModel):
    brief: ManagerBrief


class AnswerSubmission(BaseModel):
    """The manager's replies.

    The only route by which an answer enters a session. No advisory output can
    reach this, so the model cannot invent or alter what the manager said.
    """

    answers: dict[str, str] = Field(
        default={}, description="question id to the manager's own words"
    )
    skipped: list[str] = Field(default=[], description="question ids the manager declined")


def _question_view(session) -> list[dict[str, Any]]:
    return [
        {
            "id": qid,
            "question": text,
            "why_it_matters": why,
            "status": status.value,
        }
        for qid, text, why, status in session.all_questions()
    ]


def _session_view(session, turn: Any = None) -> dict[str, Any]:
    """What the interface renders.

    Open questions are read from session state, not from a generated summary, so
    a recommendation that forgets to mention a skipped question cannot make it
    vanish from the manager's view.
    """
    comparison = session.comparison
    recommendation = session.recommendation
    diagnosis = session.diagnosis
    context_request = session.context_request

    view: dict[str, Any] = {
        "session_id": session.id,
        "status": session.status,
        "context_id": session.brief.context_id,
        "brief": session.brief.model_dump(mode="json"),
        "diagnosis": diagnosis.model_dump(mode="json") if diagnosis else None,
        "context_request": context_request.model_dump(mode="json") if context_request else None,
        "questions": _question_view(session),
        "open_questions": [
            {"id": qid, "question": text, "status": status.value}
            for qid, text, _why, status in session.open_questions()
        ],
        "comparison": comparison.model_dump(mode="json") if comparison else None,
        "recommendation": recommendation.model_dump(mode="json") if recommendation else None,
        "awaiting_answers": session.has_pending_questions(),
        "error": None,
        "stopped_because": None,
    }

    if turn is not None:
        view["error"] = turn.error
        view["stopped_because"] = turn.stopped_because
        view["actions_taken"] = turn.actions

    return view


def _engine() -> AdvisoryEngine:
    try:
        return AdvisoryEngine(build_client())
    except ModelNotConfigured as exc:
        raise HTTPException(
            status_code=503,
            detail={
                "kind": "ModelNotConfigured",
                "message": exc.user_message,
                "details": exc.problems,
                "recoverable": False,
            },
        ) from exc


@router.post("/sessions", summary="Start an advisory session")
async def start_session(request: StartSessionRequest) -> dict[str, Any]:
    """Create a session from a brief and run the first turn.

    Editing the brief later starts a **new** session rather than revising this
    one. Revision is not implemented, and pretending otherwise would present
    fresh advice as though it were a considered change of mind.
    """
    engine = _engine()
    session = store.create(request.brief)
    turn = await engine.run_turn(session)
    return _session_view(session, turn)


@router.get("/sessions/{session_id}", summary="Current state of a session")
async def get_session(session_id: str) -> dict[str, Any]:
    try:
        session = store.get(session_id)
    except SessionStateError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc
    return _session_view(session)


@router.post("/sessions/{session_id}/answers", summary="Answer or skip clarification questions")
async def submit_answers(session_id: str, submission: AnswerSubmission) -> dict[str, Any]:
    """Record the manager's replies, then continue the session.

    A question may be answered or explicitly skipped. A skip is a decision and is
    preserved as such: it stays visible, it is never re-asked, and nothing may
    cite it as a source.
    """
    try:
        session = store.get(session_id)
    except SessionStateError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc

    engine = _engine()

    # The answers are written inside the session lock, by run_turn, so they
    # cannot change while a turn is awaiting a model response. Writing them
    # here, outside the lock, would allow advice to be generated against one set
    # of answers and committed against another.
    def record() -> None:
        session.record_answers(submission.answers, set(submission.skipped))

    try:
        turn = await engine.run_turn(session, prepare=record)
    except SessionStateError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc)}) from exc

    return _session_view(session, turn)


@router.post("/sessions/{session_id}/continue", summary="Run another advisory turn")
async def continue_session(session_id: str) -> dict[str, Any]:
    try:
        session = store.get(session_id)
    except SessionStateError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc

    engine = _engine()
    turn = await engine.run_turn(session)
    return _session_view(session, turn)


@router.get("/sessions/{session_id}/trace", summary="Developer trace for a session")
async def session_trace(session_id: str) -> dict[str, Any]:
    """Which prompt version produced what, and what it cost.

    Diagnostics, not part of the manager's workflow.
    """
    try:
        session = store.get(session_id)
    except SessionStateError as exc:
        raise HTTPException(status_code=404, detail={"message": str(exc)}) from exc

    return {
        "session_id": session.id,
        "turn": session.turn,
        "last_budget": session.last_budget,
        "last_error": session.last_error,
        "permitted_now": sorted(a.value for a in permitted_actions(session)),
        # Every provider request attempted, in order: selector calls, actions,
        # repairs, rejections and failures. Usage is reported only where the
        # provider actually gave it, and never invented for a request that
        # failed or was cancelled.
        "attempts": [attempt.as_dict() for attempt in session.attempts],
        # What the application accepted and now holds as advice.
        "records": [
            {
                "action": record.action.value,
                "turn": record.turn,
                "created_at": record.created_at,
                "prompt": record.prompt_trace,
                "usage": record.usage,
                "repaired": record.repaired,
                "repair_usage": record.repair_usage,
            }
            for record in session.records
        ],
    }


__all__ = ["router", "ModelError", "AnswerStatus"]
