"""API-facing schemas for OpenAI Structured Outputs.

**Why this layer exists.**

Structured Outputs accepts a subset of JSON Schema, and strict mode adds rules
of its own: every property must appear in ``required``, and
``additionalProperties`` must be ``false`` on every object. Our application
contracts satisfy neither. They carry defaults throughout, which means optional
properties, and they use pattern-constrained identifiers, minimum text lengths
and a three-question cap.

So the wire models here are a **deliberately conservative subset** we chose:
plain strings, every field required, optionals expressed as ``X | None``, no
defaults, no constraints, no numeric types at all. Nothing in them depends on a
keyword whose support we are unsure of.

**What we know, and how well.** The precise per-keyword support list could not
be retrieved from the official guide when this was written: the page truncated
before its supported-schemas section. The project owner reports that the
documentation distinguishes additional restrictions that apply to fine-tuned
models, which means a blanket claim that ``pattern``, string-length bounds,
array-length bounds and numeric bounds are universally rejected would be wrong,
and an earlier version of this docstring made exactly that claim.

We therefore do not assert what the service accepts. We assert only what we
chose to send, and why: a subset narrow enough that the question does not arise.

**Three different things, kept apart.**

1. *Our chosen subset* is what these models use. A decision, not a discovery.
2. *Local schema checks* confirm that these models convert through the SDK's
   strict-schema helper without emitting keywords outside that subset. This runs
   offline and proves nothing about the service.
3. *Actual service acceptance* is established only when OpenAI accepts a request
   carrying one of these schemas. **That has not yet been observed.** No live
   request has been made.

Output crosses from wire to application contract in :mod:`app.core.validation`,
where the real rules run. **The API cannot enforce our rules, and this layer
does not pretend it can.** A model returning four clarification questions
produces a valid wire object and is then rejected by the application contract,
which is the correct outcome and is covered by a test.
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
