"""Whether the application is configured well enough to attempt a model call.

**This module answers one narrow question: is there local configuration that
looks usable?** It does not, and cannot, answer whether the credentials work.
Nothing short of a completed request to the provider establishes that, so every
name and message here says "configured locally" rather than "connected" or
"authenticated".

The distinction matters in practice. A manager who sees "connected" and then
gets an authentication failure on their first session has been misled by the
status indicator, which is worse than having no indicator.

One implementation, used by both the health endpoint and client construction,
so the two can never disagree about whether the application is set up.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.config import DEFAULT_MODEL_NAME, settings

#: Providers with an adapter. Anything else is a configuration error rather
#: than something to attempt and fail at.
SUPPORTED_PROVIDERS = frozenset({"openai"})

#: Values that are obviously not a key. The committed `.env.example` placeholder
#: is the important one: copying the example and forgetting to edit it is the
#: single most likely setup mistake, and it previously read as configured.
#:
#: Compared case-insensitively after stripping whitespace.
PLACEHOLDER_VALUES = frozenset(
    {
        "your-openai-api-key-here",
        "your-api-key-here",
        "your-key-here",
        "your_api_key_here",
        "sk-...",
        "sk-xxx",
        "sk-your-key",
        "changeme",
        "change-me",
        "replace-me",
        "replaceme",
        "todo",
        "tbd",
        "none",
        "null",
        "xxx",
        "xxxx",
        "example",
        "placeholder",
    }
)


def _looks_like_a_placeholder(value: str) -> bool:
    """Whether a value is plainly not a real credential.

    Deliberately not a format check. Provider key formats change, and a rule
    that rejects a valid key is worse than one that lets an invalid key reach
    the provider, where it fails with a clear message. This catches only values
    that no real key could be: the documented placeholders, and angle-bracket
    templates such as ``<your key>``.
    """
    stripped = value.strip()
    if not stripped:
        return True
    if stripped.lower() in PLACEHOLDER_VALUES:
        return True
    return stripped.startswith("<") and stripped.endswith(">")


@dataclass(frozen=True)
class ConfigurationStatus:
    """The result of checking local configuration.

    ``configured_locally`` means the settings look usable, nothing more.
    """

    configured_locally: bool
    provider: str | None
    model: str
    problems: list[str] = field(default_factory=list)

    #: Kept alongside the status so every consumer repeats the same caveat
    #: rather than inventing its own wording.
    note: str = (
        "Local configuration presence only. This does not mean the credentials are valid: "
        "only a completed request to the provider establishes that."
    )

    def as_dict(self) -> dict[str, object]:
        return {
            "configured_locally": self.configured_locally,
            "provider": self.provider,
            "model": self.model,
            "problems": self.problems,
            "note": self.note,
        }

    def problem_summary(self) -> str:
        if not self.problems:
            return "Configuration looks usable."
        return " ".join(self.problems)


def check_configuration() -> ConfigurationStatus:
    """Inspect the current settings.

    Reads ``settings`` at call time rather than at import, so a test or a
    restart with different values is reflected immediately.
    """
    problems: list[str] = []

    raw_provider = (settings.model_provider or "").strip()
    provider = raw_provider.lower() or None

    if not provider:
        problems.append("MODEL_PROVIDER is not set. Set it to 'openai'.")
    elif provider not in SUPPORTED_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_PROVIDERS))
        problems.append(
            f"MODEL_PROVIDER is '{raw_provider}', which has no adapter. Supported: {supported}."
        )

    raw_key = settings.model_api_key or ""
    if not raw_key.strip():
        problems.append("MODEL_API_KEY is not set.")
    elif _looks_like_a_placeholder(raw_key):
        problems.append(
            "MODEL_API_KEY still holds a placeholder value. Replace it in your local .env "
            "with a real key."
        )

    model = (settings.model_name or "").strip() or DEFAULT_MODEL_NAME

    return ConfigurationStatus(
        configured_locally=not problems,
        provider=provider,
        model=model,
        problems=problems,
    )
