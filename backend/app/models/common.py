"""Shared primitives for the data contracts.

Two ideas carry most of the weight here.

**Stable identifiers.** Every addressable thing a manager supplies has a typed
identifier with a prefix, so a reference is readable on its own and a mistyped
identifier fails structurally rather than pointing at the wrong object.

**Explicit unknowns.** Where a value may genuinely be absent, the field is
required and nullable rather than optional with a default. The producer has to
write ``null`` deliberately. Nothing is quietly filled in, and there are no
numeric placeholders anywhere in these contracts.

What the validation in this package does and does not establish is stated in
docs/decisions.md, D-016. In short: it checks shape and referential integrity.
It does not check whether anything is true.
"""

from __future__ import annotations

from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints

# --- Identifiers ----------------------------------------------------------
#
# Prefixes are part of the identifier, so a reference carries its own kind and a
# reader can tell an objective from an initiative without a lookup.

ObjectiveId = Annotated[str, StringConstraints(pattern=r"^OBJ-[A-Za-z0-9][A-Za-z0-9_-]*$")]
ConstraintId = Annotated[str, StringConstraints(pattern=r"^CON-[A-Za-z0-9][A-Za-z0-9_-]*$")]
InitiativeId = Annotated[str, StringConstraints(pattern=r"^INI-[A-Za-z0-9][A-Za-z0-9_-]*$")]
QuestionId = Annotated[str, StringConstraints(pattern=r"^Q-[A-Za-z0-9][A-Za-z0-9_-]*$")]
ContextId = Annotated[str, StringConstraints(pattern=r"^CTX-[A-Za-z0-9][A-Za-z0-9_-]*$")]

# Free text that must actually say something. Used wherever an empty string
# would be a silent way of declining to answer.
NonEmptyText = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class StrictModel(BaseModel):
    """Base for every contract in this package.

    ``extra="forbid"`` matters more than it looks. When a model returns a field
    we did not declare, that is a signal worth surfacing rather than dropping:
    it usually means the prompt and the contract have drifted apart.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


# --- Source references ----------------------------------------------------


class SourceKind(str, Enum):
    """The kinds of input a claim can be traced back to."""

    OBJECTIVE = "brief.objective"
    CONSTRAINT = "brief.constraint"
    INITIATIVE = "brief.initiative"
    CLARIFICATION_ANSWER = "clarification.answer"


class SourceRef(StrictModel):
    """A lightweight pointer from a claim to the input it rests on.

    Deliberately thin: a kind and an identifier. It says "this claim came from
    that input," and nothing more. It does not quote the input, score the
    strength of the link, or assert that the input actually supports the claim.

    A reference check confirms the identifier exists. That is a real property,
    and it is the only one being claimed.
    """

    kind: SourceKind
    ref_id: str

    def as_key(self) -> tuple[str, str]:
        return (self.kind.value, self.ref_id)

    def __str__(self) -> str:  # pragma: no cover - convenience only
        return f"{self.kind.value}:{self.ref_id}"


class Claim(StrictModel):
    """A statement plus the inputs it is traced to.

    ``sources`` may be empty, and an empty list is meaningful rather than
    missing: it marks a statement that does not rest on anything the manager
    supplied. For an assumption that is the normal case and is exactly what we
    want visible.
    """

    statement: NonEmptyText
    sources: list[SourceRef] = []
