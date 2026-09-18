"""API-facing schemas for OpenAI Structured Outputs.

**Why this layer exists.**

Structured Outputs accepts a restricted subset of JSON Schema. It does not
support ``minLength``, ``maxLength``, ``pattern``, ``minItems``, ``maxItems``,
``default``, or numeric bounds, and in strict mode every property must appear in
``required``.

Our application contracts in this package use all of those. Identifiers are
pattern-constrained, text fields have minimum lengths, a clarification batch is
capped at three questions, and many fields carry defaults. Sending them to the
API would mean either a rejected schema or silently dropped constraints.

So there are two layers, deliberately:

- **Wire models, here.** Compatible by construction. Plain strings, every field
  required, optionals as ``X | None``, no defaults, no constraints. These are
  what the model is asked to produce.
- **Application contracts, everywhere else.** Strict. These are what the
  application accepts.

Output crosses from one to the other through :mod:`app.core.validation`, where
the real rules run. **The API cannot enforce our rules, and this layer does not
pretend it can.** A model that returns four clarification questions produces a
valid wire object and is then rejected by the application contract, which is the
correct outcome and is covered by a test.

A compatibility test asserts that every model here converts to a strict schema
with no unsupported keyword, and that wire and application shapes have not
drifted apart.
"""

from __future__ import annotations

from app.models.common import SourceKind, StrictModel
from app.models.recommendation import Stance

# --- Shared pieces --------------------------------------------------------


class WireSourceRef(StrictModel):
    kind: SourceKind
    ref_id: str


class WireClaim(StrictModel):
    statement: str
    sources: list[WireSourceRef]


# --- next_action ----------------------------------------------------------


class WireNextAction(StrictModel):
    action: str
    reasoning: str


# --- diagnose -------------------------------------------------------------


class WireGap(StrictModel):
    description: str
    why_it_matters: str
    relates_to: list[WireSourceRef]


class WireDiagnosis(StrictModel):
    context_id: str
    gaps: list[WireGap]
    contradictions: list[WireGap]
    unstated_assumptions: list[WireGap]
    summary: str


# --- request_context ------------------------------------------------------


class WireMissingInput(StrictModel):
    field: str
    why_required: str


class WireContextRequest(StrictModel):
    missing: list[WireMissingInput]
    message: str


# --- ask_clarification ----------------------------------------------------


class WireClarificationQuestion(StrictModel):
    id: str
    question: str
    why_it_matters: str
    relates_to: list[WireSourceRef]


class WireClarificationBatch(StrictModel):
    questions: list[WireClarificationQuestion]


# --- compare --------------------------------------------------------------


class WireMissingEvidence(StrictModel):
    description: str
    why_it_matters: str
    # Nullable rather than absent: the model must say it sees no route, rather
    # than omitting the field and leaving us to guess which it meant.
    how_it_could_be_resolved: str | None


class WireInitiativeComparison(StrictModel):
    initiative_id: str
    stated_facts: list[WireClaim]
    assumptions: list[WireClaim]
    missing_evidence: list[WireMissingEvidence]
    feasibility_constraints: list[WireClaim]
    trade_offs: list[WireClaim]


class WireComparison(StrictModel):
    context_id: str
    criteria_considered: list[str]
    initiatives: list[WireInitiativeComparison]
    cross_cutting_notes: list[WireClaim]


# --- recommend ------------------------------------------------------------


class WireRecommendedItem(StrictModel):
    initiative_id: str
    stance: Stance
    rationale: str
    supported_by: list[WireSourceRef]
    rests_on_assumptions: list[str]


class WireRisk(StrictModel):
    description: str
    consequence_if_realised: str
    early_signal: str | None


class WireFirstAction(StrictModel):
    action: str
    purpose: str
    resolves_unknown: str | None


class WireRecommendation(StrictModel):
    context_id: str
    summary: str
    items: list[WireRecommendedItem]
    risks: list[WireRisk]
    first_actions: list[WireFirstAction]
    open_unknowns: list[str]
    confidence_note: str
