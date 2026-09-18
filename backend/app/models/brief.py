"""The manager's brief: what they want, what limits them, what they are weighing.

This is the one contract the manager fills rather than the model. It is
deliberately tolerant about completeness and strict about identity. A brief is
allowed to be incomplete, because an incomplete brief is the normal starting
point and the application's job is to notice and ask. What it is not allowed to
be is ambiguous about which objective or initiative a later claim refers to.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from app.models.common import (
    ConstraintId,
    ContextId,
    InitiativeId,
    NonEmptyText,
    ObjectiveId,
    StrictModel,
)


class Objective(StrictModel):
    """Something the manager is trying to achieve."""

    id: ObjectiveId
    statement: NonEmptyText
    # Why this matters to them. Required but nullable: a manager who has not
    # said must produce an explicit null rather than an empty string, so
    # "not stated" is distinguishable from "stated as nothing".
    rationale: str | None = Field(
        description="The manager's own reason, or null if they did not give one",
    )


class Constraint(StrictModel):
    """A limit the advice has to respect.

    ``value`` is free text on purpose. A budget may be "around 200k", a timeline
    "before the audit in Q3", and a headcount "two engineers, maybe three". A
    typed number would force a precision the manager did not offer, and a
    missing number would need a default, which is exactly what we refuse to do.
    """

    id: ConstraintId
    kind: NonEmptyText = Field(
        description="What sort of limit this is, for example budget, timeline, headcount, regulatory",
    )
    value: str | None = Field(
        description="The limit as the manager expressed it, or null if they named the kind but not the value",
    )
    notes: str | None = Field(default=None, description="Optional elaboration")


class Initiative(StrictModel):
    """A candidate the manager is considering."""

    id: InitiativeId
    name: NonEmptyText
    description: str | None = Field(
        description="What it involves, or null if the manager has not said",
    )
    # Which objectives the manager believes this serves. Their belief, not an
    # assessment: the advisor may disagree, and that disagreement belongs in a
    # comparison rather than here.
    claimed_objectives: list[ObjectiveId] = []


class ManagerBrief(StrictModel):
    """A snapshot of the manager's situation at one point in time.

    Carries a ``context_id`` because a revision has to name the context it moved
    from and the one it moved to. Without a stable identity for the snapshot,
    "what changed" cannot be stated precisely.
    """

    context_id: ContextId
    organisation: NonEmptyText = Field(description="Fictional organisation name for the scenario")
    situation: str | None = Field(
        description="Free-text background, or null if none was given",
    )
    objectives: list[Objective] = []
    constraints: list[Constraint] = []
    initiatives: list[Initiative] = []

    @model_validator(mode="after")
    def _identifiers_are_unique_and_resolvable(self) -> ManagerBrief:
        """Structural integrity only: unique ids, and internal links that resolve.

        No judgement about whether the brief is any good. A brief with no
        objectives is valid here and is a problem for the advisor to raise, not
        for a validator to reject.
        """
        for label, ids in (
            ("objective", [o.id for o in self.objectives]),
            ("constraint", [c.id for c in self.constraints]),
            ("initiative", [i.id for i in self.initiatives]),
        ):
            duplicates = sorted({i for i in ids if ids.count(i) > 1})
            if duplicates:
                raise ValueError(f"duplicate {label} identifiers: {', '.join(duplicates)}")

        known_objectives = {o.id for o in self.objectives}
        for initiative in self.initiatives:
            unknown = [o for o in initiative.claimed_objectives if o not in known_objectives]
            if unknown:
                raise ValueError(
                    f"initiative {initiative.id} claims unknown objectives: {', '.join(sorted(unknown))}"
                )
        return self

    # --- Convenience lookups, used by the reference index ------------------

    def objective_ids(self) -> set[str]:
        return {o.id for o in self.objectives}

    def constraint_ids(self) -> set[str]:
        return {c.id for c in self.constraints}

    def initiative_ids(self) -> set[str]:
        return {i.id for i in self.initiatives}
