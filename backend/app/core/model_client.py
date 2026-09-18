"""Model access.

One interface, one real adapter. The adapter talks to OpenAI's Responses API
using native Structured Outputs, and knows nothing about advisory logic.

Two rules govern everything here:

**A failed call is a failure.** It raises. It is never replaced by sample
content, a fixture, a cached answer or a plausible default. An application that
quietly substitutes canned output for a failed call is lying about what it did,
which is worse than an error message.

**Every failure mode is named.** Missing credentials, authentication, rate
limits, timeouts, connection loss, refusals and truncated output each map to a
distinct exception carrying whether a retry could help. Nothing is swallowed
into a generic "something went wrong".

Retries are handled in exactly one place. The SDK's own retry loop is disabled,
because a retry the application cannot see is a request it cannot budget for.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

import openai
from pydantic import BaseModel

from app.config import settings

TWire = TypeVar("TWire", bound=BaseModel)


# --- Failures -------------------------------------------------------------


class ModelError(RuntimeError):
    """Base for every model access failure.

    ``recoverable`` says whether the manager could reasonably try again. It
    drives what the interface offers, not an automatic retry.
    """

    recoverable = False
    user_message = "The advisor could not complete this step."

    def __init__(self, detail: str = "") -> None:
        super().__init__(detail or self.user_message)
        self.detail = detail


class ModelNotConfigured(ModelError):
    user_message = (
        "No model provider is configured. Set MODEL_PROVIDER, MODEL_NAME and MODEL_API_KEY "
        "in a local .env file, then restart the backend."
    )


class ModelAuthError(ModelError):
    user_message = "The model provider rejected the credentials. Check MODEL_API_KEY."


class ModelRateLimited(ModelError):
    recoverable = True
    user_message = "The model provider is rate limiting requests. Wait a moment and try again."


class ModelTimeout(ModelError):
    recoverable = True
    user_message = "The model provider did not respond in time. Try again."


class ModelUnavailable(ModelError):
    recoverable = True
    user_message = "Could not reach the model provider. Check the connection and try again."


class ModelRefused(ModelError):
    """The model declined to answer. Not a bug, and not retried."""

    user_message = "The advisor declined to answer this step."


class ModelOutputIncomplete(ModelError):
    """Output was cut off, usually by the token ceiling. The result is unusable."""

    recoverable = True
    user_message = "The advisor's answer was cut off before it finished."


class ModelRequestInvalid(ModelError):
    """The request itself was rejected, typically an unsupported schema or model."""

    user_message = "The request sent to the model provider was rejected."


# --- Result ---------------------------------------------------------------


@dataclass(frozen=True)
class ModelCall:
    """One completed call, with what it cost and what produced it."""

    parsed: BaseModel
    model: str
    input_tokens: int | None
    output_tokens: int | None
    total_tokens: int | None
    duration_ms: int
    response_id: str | None

    def usage(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "duration_ms": self.duration_ms,
            "response_id": self.response_id,
        }


class ModelClient(Protocol):
    """What the advisory loop depends on.

    Deliberately narrow. Tests substitute a deterministic double implementing
    this and nothing else, so no test needs a network or a key.
    """

    @property
    def model_name(self) -> str: ...

    async def complete(
        self,
        *,
        instructions: str,
        input_text: str,
        schema: type[TWire],
        schema_name: str,
    ) -> ModelCall: ...


# --- OpenAI adapter -------------------------------------------------------


class OpenAIClient:
    """Adapter over the OpenAI Responses API with Structured Outputs.

    The schema passed here must be a wire model from :mod:`app.models.wire`.
    Application contracts carry constraints the Structured Outputs schema subset
    does not accept, and sending one would be rejected by the API. The strict
    contracts are applied afterwards, in the validation boundary.
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
        max_output_tokens: int | None = None,
    ) -> None:
        key = api_key or settings.model_api_key
        if not key:
            raise ModelNotConfigured(
                "MODEL_API_KEY is not set. The backend starts without it, but no advisory "
                "step can run until it is configured."
            )

        self._model = model or settings.model_name or settings.default_model_name
        self._max_output_tokens = max_output_tokens or settings.max_output_tokens

        self._client = openai.AsyncOpenAI(
            api_key=key,
            timeout=timeout_seconds or settings.model_timeout_seconds,
            # The application counts every request against a budget, so the SDK
            # must not issue any the application did not ask for. Retrying is a
            # decision made above this layer or not at all.
            max_retries=0,
        )

    @property
    def model_name(self) -> str:
        return self._model

    async def complete(
        self,
        *,
        instructions: str,
        input_text: str,
        schema: type[TWire],
        schema_name: str,
    ) -> ModelCall:
        started = time.monotonic()

        try:
            response = await self._client.responses.parse(
                model=self._model,
                instructions=instructions,
                input=input_text,
                text_format=schema,
                max_output_tokens=self._max_output_tokens,
            )
        except openai.AuthenticationError as exc:
            raise ModelAuthError(str(exc)) from exc
        except openai.RateLimitError as exc:
            raise ModelRateLimited(str(exc)) from exc
        except openai.APITimeoutError as exc:
            raise ModelTimeout(str(exc)) from exc
        except openai.APIConnectionError as exc:
            raise ModelUnavailable(str(exc)) from exc
        except openai.BadRequestError as exc:
            # Usually an unsupported schema or an unknown model. Surfaced
            # distinctly because it is a defect on our side, not the provider's.
            raise ModelRequestInvalid(str(exc)) from exc
        except openai.APIStatusError as exc:
            recoverable = exc.status_code >= 500
            error = ModelUnavailable(str(exc)) if recoverable else ModelRequestInvalid(str(exc))
            raise error from exc

        duration_ms = int((time.monotonic() - started) * 1000)

        # Truncated output is not partially usable. A comparison missing its
        # last initiative would validate as a comparison.
        if getattr(response, "status", None) == "incomplete":
            reason = getattr(getattr(response, "incomplete_details", None), "reason", "unknown")
            raise ModelOutputIncomplete(f"response incomplete: {reason}")

        refusal = self._find_refusal(response)
        if refusal:
            raise ModelRefused(refusal)

        parsed = getattr(response, "output_parsed", None)
        if parsed is None:
            raise ModelOutputIncomplete(
                f"the provider returned no parsed output for {schema_name}"
            )

        usage = getattr(response, "usage", None)
        return ModelCall(
            parsed=parsed,
            model=self._model,
            input_tokens=getattr(usage, "input_tokens", None),
            output_tokens=getattr(usage, "output_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
            duration_ms=duration_ms,
            response_id=getattr(response, "id", None),
        )

    @staticmethod
    def _find_refusal(response: Any) -> str | None:
        """A refusal arrives as content, not as an exception."""
        for item in getattr(response, "output", None) or []:
            for content in getattr(item, "content", None) or []:
                if getattr(content, "type", None) == "refusal":
                    return getattr(content, "refusal", "the model declined to answer")
        return None


def build_client() -> ModelClient:
    """Construct the configured client, or explain why it cannot be built.

    Raises :class:`ModelNotConfigured` rather than returning a stub. There is no
    silent fallback: the application starts without credentials, and the failure
    appears when an advisory step is attempted, where the manager can see it.
    """
    provider = (settings.model_provider or "").strip().lower()

    if not provider:
        raise ModelNotConfigured(
            "MODEL_PROVIDER is not set. Set it to 'openai' in a local .env file."
        )
    if provider != "openai":
        raise ModelNotConfigured(
            f"MODEL_PROVIDER is '{provider}', but only 'openai' is implemented."
        )

    return OpenAIClient()
