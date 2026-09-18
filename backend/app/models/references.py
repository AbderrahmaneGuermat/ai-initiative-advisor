"""Referential integrity for source references.

A claim may point at an objective, a constraint, an initiative or a clarification
answer. This module checks that the thing it points at exists.

**What this establishes.** That an identifier resolves. Nothing else.

**What it does not establish.** That the cited input supports the claim, that the
claim is true, or that the citation is the right one. A claim citing an
unrelated objective passes every check here. See docs/decisions.md, D-016.

The check lives outside the individual models because a model cannot see the
brief it was produced against. Keeping it a separate, explicit call also keeps
it honest: it is a step someone chose to run, not a property the type system
quietly implies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable

from pydantic import BaseModel

from app.models.brief import ManagerBrief
from app.models.clarification import ClarificationRound
from app.models.common import SourceKind, SourceRef


@dataclass(frozen=True)
class ReferenceIndex:
    """Everything a claim is allowed to cite, for one session.

    Only *answered* clarification questions are citable. A skipped question
    produced no input, so a claim resting on it would be resting on nothing.
    """

    objectives: frozenset[str] = field(default_factory=frozenset)
    constraints: frozenset[str] = field(default_factory=frozenset)
    initiatives: frozenset[str] = field(default_factory=frozenset)
    answered_questions: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def build(
        cls,
        brief: ManagerBrief,
        clarification_rounds: Iterable[ClarificationRound] = (),
    ) -> ReferenceIndex:
        answered: set[str] = set()
        for round_ in clarification_rounds:
            answered |= round_.answered_ids()
        return cls(
            objectives=frozenset(brief.objective_ids()),
            constraints=frozenset(brief.constraint_ids()),
            initiatives=frozenset(brief.initiative_ids()),
            answered_questions=frozenset(answered),
        )

    def known_ids(self, kind: SourceKind) -> frozenset[str]:
        return {
            SourceKind.OBJECTIVE: self.objectives,
            SourceKind.CONSTRAINT: self.constraints,
            SourceKind.INITIATIVE: self.initiatives,
            SourceKind.CLARIFICATION_ANSWER: self.answered_questions,
        }[kind]

    def resolves(self, ref: SourceRef) -> bool:
        return ref.ref_id in self.known_ids(ref.kind)


def collect_source_refs(value: Any) -> list[SourceRef]:
    """Every source reference anywhere inside a payload.

    Walks models, lists, tuples and dicts. Written generically so a new contract
    that carries references is covered without anyone remembering to update this
    function.
    """
    found: list[SourceRef] = []

    if isinstance(value, SourceRef):
        found.append(value)
    elif isinstance(value, BaseModel):
        for name in type(value).model_fields:
            found.extend(collect_source_refs(getattr(value, name)))
    elif isinstance(value, (list, tuple, set, frozenset)):
        for item in value:
            found.extend(collect_source_refs(item))
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(collect_source_refs(item))

    return found


def unresolved_references(payload: Any, index: ReferenceIndex) -> list[SourceRef]:
    """References in ``payload`` that do not resolve against ``index``.

    Returns them rather than raising, so a caller can decide what to do. During
    an advisory turn an unresolved reference is worth surfacing to the manager;
    in a test it is worth failing on. That decision is not this function's.
    """
    return [ref for ref in collect_source_refs(payload) if not index.resolves(ref)]


class UnresolvedReferenceError(ValueError):
    """Raised by :func:`require_resolvable_references`."""

    def __init__(self, unresolved: list[SourceRef]) -> None:
        listed = ", ".join(str(ref) for ref in unresolved)
        super().__init__(f"payload cites identifiers that do not exist: {listed}")
        self.unresolved = unresolved


def require_resolvable_references(payload: Any, index: ReferenceIndex) -> None:
    """Raise if any reference in ``payload`` fails to resolve.

    A structural check. Passing it means every citation points at something real,
    and says nothing at all about whether the citation is apt.
    """
    unresolved = unresolved_references(payload, index)
    if unresolved:
        raise UnresolvedReferenceError(unresolved)


def known_initiative_ids_only(referenced: Iterable[str], index: ReferenceIndex) -> list[str]:
    """Initiative identifiers from ``referenced`` that the brief does not contain.

    Used where a contract names initiatives directly rather than through a
    source reference, as a recommendation does.
    """
    return sorted(set(referenced) - index.initiatives)
