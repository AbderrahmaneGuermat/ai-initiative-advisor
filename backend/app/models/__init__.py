"""Data contracts for the advisory exchange.

These are declarations of shape, not behaviour. No module here calls a model,
holds state, or decides anything about which initiative is better. Validators
check structure and referential integrity only; business judgement stays in the
runtime prompts, which are not written yet.

What validation here does and does not establish is set out in
docs/decisions.md, D-016. Briefly: it checks that payloads have the declared
shape and that cited identifiers exist. It does not check that anything is true.
"""

from app.models.actions import (
    ACTION_OUTPUT_CONTRACTS,
    ACTION_PROMPTS,
    AdvisoryAction,
    AwaitUser,
    ContextRequest,
    Diagnosis,
    Gap,
    MissingInput,
    NextAction,
    output_contract_for,
)
from app.models.brief import Constraint, Initiative, ManagerBrief, Objective
from app.models.clarification import (
    MAX_QUESTIONS_PER_BATCH,
    AnswerStatus,
    ClarificationBatch,
    ClarificationQuestion,
    ClarificationResponse,
    ClarificationRound,
)
from app.models.common import (
    Claim,
    ConstraintId,
    ContextId,
    InitiativeId,
    NonEmptyText,
    ObjectiveId,
    QuestionId,
    SourceKind,
    SourceRef,
    StrictModel,
)
from app.models.comparison import Comparison, InitiativeComparison, MissingEvidence
from app.models.recommendation import (
    ConstraintChange,
    FirstAction,
    RecommendedItem,
    Recommendation,
    Revision,
    Risk,
    Stance,
    StanceChange,
)
from app.models.references import (
    ReferenceIndex,
    UnresolvedReferenceError,
    collect_source_refs,
    known_initiative_ids_only,
    require_resolvable_references,
    unresolved_references,
)

__all__ = [
    "ACTION_OUTPUT_CONTRACTS",
    "ACTION_PROMPTS",
    "MAX_QUESTIONS_PER_BATCH",
    "AdvisoryAction",
    "AnswerStatus",
    "AwaitUser",
    "Claim",
    "ClarificationBatch",
    "ClarificationQuestion",
    "ClarificationResponse",
    "ClarificationRound",
    "Comparison",
    "Constraint",
    "ConstraintChange",
    "ConstraintId",
    "ContextId",
    "ContextRequest",
    "Diagnosis",
    "FirstAction",
    "Gap",
    "Initiative",
    "InitiativeComparison",
    "InitiativeId",
    "ManagerBrief",
    "MissingEvidence",
    "MissingInput",
    "NextAction",
    "NonEmptyText",
    "Objective",
    "ObjectiveId",
    "QuestionId",
    "Recommendation",
    "RecommendedItem",
    "ReferenceIndex",
    "Revision",
    "Risk",
    "SourceKind",
    "SourceRef",
    "Stance",
    "StanceChange",
    "StrictModel",
    "UnresolvedReferenceError",
    "collect_source_refs",
    "known_initiative_ids_only",
    "output_contract_for",
    "require_resolvable_references",
    "unresolved_references",
]
