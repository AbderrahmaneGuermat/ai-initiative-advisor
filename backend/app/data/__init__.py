"""Access to the hand-authored fictional sample data.

Read-only. These files are fiction written by a person to exercise the
contracts and to give the interface something to load. They are **not** recorded
model responses and are never presented as one: the scenario endpoint labels
them, and the interface labels them again.

Annotation keys beginning with an underscore carry that labelling inside the
files themselves. They are stripped before validation, because the contracts
forbid undeclared fields and the annotations exist for human readers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.models import ManagerBrief

DATA_DIR = Path(__file__).resolve().parent
SCENARIOS_DIR = DATA_DIR / "scenarios"
EXAMPLES_DIR = DATA_DIR / "examples"

SAMPLE_SCENARIO = "larkfield-freight.json"


def strip_annotations(value: Any) -> Any:
    """Remove keys beginning with an underscore, at any depth."""
    if isinstance(value, dict):
        return {k: strip_annotations(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [strip_annotations(item) for item in value]
    return value


def load_json(path: Path) -> dict[str, Any]:
    return strip_annotations(json.loads(path.read_text(encoding="utf-8")))


def sample_scenario_id() -> str:
    return SAMPLE_SCENARIO.removesuffix(".json")


def load_sample_brief() -> ManagerBrief:
    """The fictional brief, validated against the contract before it is served."""
    return ManagerBrief.model_validate(load_json(SCENARIOS_DIR / SAMPLE_SCENARIO))
