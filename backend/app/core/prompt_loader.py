"""Loads runtime prompts from disk.

Prompts are read from ``backend/prompts/`` **at the moment they are executed**,
never cached for the lifetime of the process. Editing a prompt file changes the
next advisory turn with no restart and no Python edit. That is the property the
method claims, and reading from disk each time is what makes it testable rather
than asserted.

Every load records a SHA-256 hash of the file contents. The hash goes into the
session's trace, so a later reader can tell which version of a prompt produced a
given output, even if the file has changed since.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import yaml

PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"

#: Front matter keys every prompt must declare. Required so that a prompt file
#: states its own contract rather than leaving a reader to infer it.
REQUIRED_KEYS = ("id", "version", "role", "inputs", "outputs", "constraints")


class PromptError(RuntimeError):
    """A prompt file is missing or malformed."""


@dataclass(frozen=True)
class LoadedPrompt:
    """One prompt file, as read for a single execution."""

    path: str
    id: str
    version: str
    role: str
    inputs: list[str]
    outputs: str
    constraints: list[str]
    body: str
    content_hash: str

    @property
    def short_hash(self) -> str:
        return self.content_hash[:12]

    def trace(self) -> dict[str, str]:
        """What gets recorded alongside any output this prompt produced."""
        return {
            "prompt_id": self.id,
            "prompt_version": self.version,
            "prompt_path": self.path,
            "content_hash": self.short_hash,
        }


def _split_front_matter(raw: str, relative_path: str) -> tuple[dict, str]:
    if not raw.startswith("---"):
        raise PromptError(f"{relative_path}: missing YAML front matter")

    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise PromptError(f"{relative_path}: front matter is not terminated by a second '---'")

    try:
        meta = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as exc:
        raise PromptError(f"{relative_path}: front matter is not valid YAML: {exc}") from exc

    if not isinstance(meta, dict):
        raise PromptError(f"{relative_path}: front matter must be a mapping")

    return meta, parts[2].strip()


def load_prompt(relative_path: str, prompts_dir: Path | None = None) -> LoadedPrompt:
    """Read one prompt file from disk, now.

    ``relative_path`` is relative to ``backend/prompts``, for example
    ``actions/compare.md``.
    """
    base = prompts_dir or PROMPTS_DIR
    path = base / relative_path

    if not path.is_file():
        raise PromptError(f"prompt file not found: {relative_path} (looked in {base})")

    raw = path.read_text(encoding="utf-8")
    meta, body = _split_front_matter(raw, relative_path)

    missing = [key for key in REQUIRED_KEYS if key not in meta]
    if missing:
        raise PromptError(f"{relative_path}: front matter is missing {', '.join(missing)}")

    if not body:
        raise PromptError(f"{relative_path}: prompt body is empty")

    def as_list(value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return [str(value)]

    return LoadedPrompt(
        path=relative_path,
        id=str(meta["id"]),
        version=str(meta["version"]),
        role=str(meta["role"]),
        inputs=as_list(meta["inputs"]),
        outputs=str(meta["outputs"]),
        constraints=as_list(meta["constraints"]),
        body=body,
        # Hash the whole file, front matter included. A version bump with no
        # body change is still a change worth being able to see.
        content_hash=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
    )


def available_prompts(prompts_dir: Path | None = None) -> list[str]:
    """Every prompt file present, as paths relative to the prompts directory."""
    base = prompts_dir or PROMPTS_DIR
    if not base.is_dir():
        return []
    return sorted(str(p.relative_to(base)).replace("\\", "/") for p in base.rglob("*.md"))
