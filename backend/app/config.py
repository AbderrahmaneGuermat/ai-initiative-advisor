"""Application configuration.

Values come from the environment, or from a ``.env`` file at the repository
root. No secret is ever hard-coded here, and no default in this file is a real
credential.

The model provider is deliberately unset by default. That decision is open
until API access is confirmed; see docs/decisions.md, D-014.
"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]

# The stage this build is at. Reported by the health endpoint so that anyone
# calling the API can tell how much of the application actually exists.
BUILD_STAGE = "advisory-flow"
APP_VERSION = "0.1.0"

#: Used when MODEL_NAME is unset. Configurable, and never switched silently:
#: if a different model is wanted, it is set here or in .env, not chosen by the
#: application at runtime.
DEFAULT_MODEL_NAME = "gpt-5-mini"


class Settings(BaseSettings):
    """Settings loaded from the environment or the repository-root .env file."""

    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Server -----------------------------------------------------------
    # The local addresses are fixed for this MVP, not configurable. The backend
    # binds 127.0.0.1:8000 in scripts/dev-backend.mjs and the dev server serves
    # 5173 in frontend/vite.config.ts. No host or port setting is declared here,
    # because nothing would read one. See docs/decisions.md, D-015.

    # Origins allowed to call the API directly. In normal development the Vite
    # dev server proxies /api, so no browser request is cross-origin and this
    # list is unused. It exists for the case where the frontend is opened
    # against the backend directly.
    cors_allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # --- Model access -----------------------------------------------------
    # The provider is OpenAI (docs/decisions.md). Read from .env or the shell.
    # The key is never returned by an endpoint, logged, or sent to the browser.
    model_provider: str | None = None
    model_name: str | None = None
    model_api_key: str | None = None

    # Reserved for an offline replay mode that is NOT implemented. The flag is
    # read but nothing acts on it. If it is ever built, replayed output must be
    # labelled as sample data and must never replace a failed live call. See
    # docs/decisions.md, D-009.
    offline_fixture_mode: bool = False

    # --- Request shaping --------------------------------------------------
    #: Ceiling on generated tokens per request. A comparison over several
    #: initiatives is the largest output this application asks for.
    max_output_tokens: int = 8000
    #: Per-request timeout in seconds, passed to the SDK.
    model_timeout_seconds: float = 120.0

    #: Wall-clock ceiling for one advisory turn.
    #:
    #: Raised from 180 to 300 after the first live run, where a turn that had
    #: already committed a comparison was cut off before it could recommend.
    #: This is operational headroom, not a performance improvement: the requests
    #: take exactly as long as they did before, and the same work now has more
    #: room to finish inside one turn.
    max_turn_seconds: float = 300.0

    #: Reasoning effort passed to the Responses API, for models that support it.
    #:
    #: Valid values per the reasoning guide are none, minimal, low, medium,
    #: high, xhigh and max, and support varies by model. Set to an empty string
    #: to omit the parameter entirely, which is the safe option if a model
    #: rejects it.
    #:
    #: Defaults to "low". The first live run spent a large share of its output
    #: tokens on reasoning for work that is mostly structured extraction and
    #: judgement over a short brief.
    model_reasoning_effort: str = "low"

    @property
    def default_model_name(self) -> str:
        return DEFAULT_MODEL_NAME

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    # There is deliberately no `model_configured` property here.
    #
    # An earlier version had one that returned true for any non-empty provider
    # and key, which meant the committed placeholder read as configured: copy
    # .env.example, forget to edit it, and the health endpoint said the advisor
    # was ready. The check now lives in app.core.configuration, is shared by the
    # health endpoint and client construction, and rejects placeholders and
    # unsupported providers. It reports local configuration presence, never
    # authentication.


settings = Settings()
