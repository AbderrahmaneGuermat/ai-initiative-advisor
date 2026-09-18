"""HTTP surface.

Skeleton stage: a health endpoint only. The advisory endpoints do not exist
yet, and nothing here calls a model.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.config import APP_VERSION, BUILD_STAGE, settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Reported by GET /api/health.

    Deliberately honest about how much of the application exists, so that a
    reviewer calling the API is not misled by a bare "ok".
    """

    status: str = Field(description="ok when the backend is serving requests")
    service: str
    version: str
    stage: str = Field(description="Build stage; 'skeleton' means no advisory logic exists yet")
    model_configured: bool = Field(
        description="Whether a model provider and key are present. The key itself is never returned."
    )
    offline_fixture_mode: bool = Field(
        description="Whether the app would replay labelled sample fixtures instead of calling a provider"
    )
    implemented: list[str] = Field(description="Capabilities that actually work today")
    not_implemented: list[str] = Field(description="Capabilities that are planned but absent")


@router.get("/health", response_model=HealthResponse, summary="Service health and build stage")
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="AI Initiative Advisor backend",
        version=APP_VERSION,
        stage=BUILD_STAGE,
        model_configured=settings.model_configured,
        offline_fixture_mode=settings.offline_fixture_mode,
        implemented=["health"],
        not_implemented=[
            "model calls",
            "runtime prompts",
            "advisory loop",
            "comparison",
            "recommendation",
            "revision",
            "sessions",
            "scenarios",
            "export",
        ],
    )
