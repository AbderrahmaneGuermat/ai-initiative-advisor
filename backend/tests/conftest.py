"""Shared test fixtures.

The sample JSON files carry keys beginning with an underscore, used to label
them as hand-authored fiction and to explain what each one demonstrates. The
contracts forbid unknown fields, so those annotation keys are stripped before
validation. Stripping is done here rather than in application code, because the
annotations exist for human readers of the repository and nothing in the
application needs them.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

DATA_DIR = Path(__file__).resolve().parents[1] / "app" / "data"
SCENARIOS = DATA_DIR / "scenarios"
EXAMPLES = DATA_DIR / "examples"


def strip_annotations(value: Any) -> Any:
    """Remove keys beginning with an underscore, at any depth."""
    if isinstance(value, dict):
        return {k: strip_annotations(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [strip_annotations(item) for item in value]
    return value


def load_sample(path: Path) -> dict[str, Any]:
    return strip_annotations(json.loads(path.read_text(encoding="utf-8")))


@pytest.fixture(scope="session")
def brief_payload() -> dict[str, Any]:
    return load_sample(SCENARIOS / "larkfield-freight.json")


@pytest.fixture(scope="session")
def clarification_payload() -> dict[str, Any]:
    return load_sample(EXAMPLES / "01-clarification-round.json")


@pytest.fixture(scope="session")
def comparison_payload() -> dict[str, Any]:
    return load_sample(EXAMPLES / "02-comparison.json")


@pytest.fixture(scope="session")
def recommendation_payload() -> dict[str, Any]:
    return load_sample(EXAMPLES / "03-recommendation.json")


@pytest.fixture(scope="session")
def revision_payload() -> dict[str, Any]:
    return load_sample(EXAMPLES / "04-revision.json")
