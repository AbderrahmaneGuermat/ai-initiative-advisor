"""The recommendation, and the revision that follows a change of constraints.

Priority is expressed as list order plus a qualitative stance. There is no rank
number and no score, because a number invented over partial information reads as
measurement and is not one.

A recommendation also carries forward what it does not know. ``open_unknowns``
is required rather than optional, so producing advice means stating what it
rests on being unknown. Advice that looks complete because its gaps were omitted
is the failure mode this contract exists to make awkward.
"""

from __future__ import annotations

from enum import Enum

from pydantic import Field, model_validator

from app.models.common import (
    Claim,
    ConstraintId,
    ContextId,
    InitiativeId,
    NonEmptyText,
    SourceRef,
    StrictModel,
)


class Stance(str, Enum):
    """Where an initiative lands. Qualitative, deliberately coarse."""

    RECOMMENDED = "recommended"
    CONSIDER_LATER = "consider_later"
    NOT_RECOMMENDED = "not_recommended"
    INSUFFICIENT_INFORMATION = "insufficient_information"


class RecommendedItem(StrictModel):
    """One initiative's place in the advice, with what that rests on."""

    initiative_id: InitiativeId
    stance: Stance
    rationale: NonEmptyText
    # Inputs this rests on. A reference check confirms the identifier exists; it
    # does not confirm the input supports the rationale.
    supported_by: list[SourceRef] = []
    # Assumptions the stance depends on, restated here rather than left in the
    # comparison, so that reading the advice alone shows what it would take to
    # overturn it.
    rests_on_assumptions: list[NonEmptyText] = []


class Risk(StrictModel):
    """Something that could make this advice wrong."""

    description: NonEmptyText
    consequence_if_realised: NonEmptyText
    early_signal: str | None = Field(
        description="What would show this is happening, or null if nothing obvious would",
    )


class FirstAction(StrictModel):
    """A concrete next step, with the reason it comes first."""

    action: NonEmptyText
    purpose: NonEmptyText
    # Which unknown this would close, if any. Nullable: not every first action
    # is about reducing uncertainty.
    resolves_unknown: str | None = Field(
        description="The missing evidence this would address, or null",
    )


class Recommendation(StrictModel):
    """The standing advice for one context."""

    context_id: ContextId
    summary: NonEmptyText
    # Order carries priority. The first item is the first thing to do.
    items: list[RecommendedItem] = Field(min_length=1)
    risks: list[Risk] = []
    first_actions: list[FirstAction] = []
    # Required, not optional. See the module docstring.
    open_unknowns: list[NonEmptyText] = Field(
        description="What remains unknown, including anything the manager skipped",
    )
    # A written statement of how far this advice can be trusted. Prose, never a
    # percentage: a confidence number here would be the same false precision
    # that weighted scoring was removed to avoid.
    confidence_note: NonEmptyText

    @model_validator(mode="after")
    def _one_entry_per_initiative(self) -> Recommendation:
        ids = [i.initiative_id for i in self.items]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"an initiative appears more than once: {', '.join(duplicates)}")
        return self

    def recommended_ids(self) -> set[str]:
        return {i.initiative_id for i in self.items}


# --- Revision -------------------------------------------------------------


class ConstraintChange(StrictModel):
    """One constraint before and after.

    Both values are required and nullable, so a constraint that gained a value
    it never had, or lost one, is expressible without a sentinel.
    """

    constraint_id: ConstraintId
    previous_value: str | None
    current_value: str | None

    @model_validator(mode="after")
    def _something_actually_changed(self) -> ConstraintChange:
        if self.previous_value == self.current_value:
            raise ValueError(
                f"{self.constraint_id} is listed as changed but both values are identical"
            )
        return self


class StanceChange(StrictModel):
    """How one initiative's standing moved, or did not."""

    initiative_id: InitiativeId
    previous_stance: Stance | None = Field(
        description="Its stance before, or null if it was not covered by the previous advice",
    )
    current_stance: Stance
    reason: NonEmptyText


class Revision(StrictModel):
    """Advice re-issued after something changed.

    Names both contexts explicitly. "What changed" is only meaningful against a
    stated before and after, and a revision that cannot say what it moved from
    is just a second opinion.

    ``held`` is required alongside ``moved``. Reporting only what moved would let
    a revision imply wholesale reconsideration when one thing shifted, and would
    hide the more interesting case: a constraint changed and the advice did not,
    which needs its own explanation.
    """

    previous_context_id: ContextId
    current_context_id: ContextId
    triggered_by: list[ConstraintChange] = Field(min_length=1)
    moved: list[StanceChange] = []
    held: list[StanceChange] = []
    explanation: NonEmptyText
    # Unknowns carried through the revision. Still required: a change of
    # constraints does not resolve anything that was unknown before it.
    open_unknowns: list[NonEmptyText]
    cross_cutting_notes: list[Claim] = []

    @model_validator(mode="after")
    def _contexts_differ_and_initiatives_appear_once(self) -> Revision:
        if self.previous_context_id == self.current_context_id:
            raise ValueError(
                "a revision must name two different contexts; "
                "identical identifiers make the change unstatable"
            )

        ids = [c.initiative_id for c in self.moved] + [c.initiative_id for c in self.held]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(
                f"initiative listed more than once across moved and held: {', '.join(duplicates)}"
            )

        for change in self.moved:
            if change.previous_stance is not None and change.previous_stance == change.current_stance:
                raise ValueError(
                    f"{change.initiative_id} is listed as moved but its stance is unchanged"
                )
        for change in self.held:
            if change.previous_stance != change.current_stance:
                raise ValueError(
                    f"{change.initiative_id} is listed as held but its stance changed"
                )
        return self
