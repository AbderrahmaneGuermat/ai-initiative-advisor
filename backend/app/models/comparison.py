"""Qualitative comparison of the candidate initiatives.

Five categories, five separate fields, no numbers. The separation is the whole
point: a reader can see which category a claim was filed under without reading
the author's mind.

To be exact about what that buys, per docs/decisions.md, D-016: the contract
forces a choice of category and records it. It cannot tell whether the choice
was honest or the statement true. A model can file an assumption under stated
facts and this contract will accept it. What the structure gives is a cheap way
for a reader to check, and somewhere consistent to look.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from app.models.common import Claim, InitiativeId, NonEmptyText, StrictModel


class MissingEvidence(StrictModel):
    """Something not known, recorded as not known.

    This is the category that stops an unknown becoming a silent zero. It has no
    value field at all, because there is no value: writing one would be
    inventing it.
    """

    description: NonEmptyText
    # What would change if this were known. Required, because "we don't know X"
    # is only useful when paired with why X matters.
    why_it_matters: NonEmptyText
    # How it could be found out. Nullable, because sometimes there is no obvious
    # route and pretending otherwise would be worse than saying so.
    how_it_could_be_resolved: str | None = Field(
        description="A way to find out, or null if none is apparent",
    )


class InitiativeComparison(StrictModel):
    """One initiative, set out across the five categories.

    Every list may be empty, and an empty list is a real statement rather than a
    gap. No trade-offs recorded means none were identified, which a reviewer can
    challenge. Forcing at least one of each would invite padding, and padded
    analysis is harder to audit than sparse analysis.
    """

    initiative_id: InitiativeId

    stated_facts: list[Claim] = Field(
        default=[],
        description="What the manager told us, traceable to their input",
    )
    assumptions: list[Claim] = Field(
        default=[],
        description="What the advisor assumed to proceed; typically carries no sources, and that is the signal",
    )
    missing_evidence: list[MissingEvidence] = Field(
        default=[],
        description="What is not known; never converted into a value",
    )
    feasibility_constraints: list[Claim] = Field(
        default=[],
        description="Limits that bound this option: budget, timeline, skills, dependencies, regulation",
    )
    trade_offs: list[Claim] = Field(
        default=[],
        description="What is given up by choosing this over the alternatives",
    )


class Comparison(StrictModel):
    """The comparison across all initiatives under consideration."""

    context_id: NonEmptyText = Field(description="The brief snapshot this comparison was made against")
    # The criteria the advisor judged relevant here. Free text, and derived per
    # situation rather than drawn from a fixed list, because which criteria
    # matter is a judgement and judgements belong in prompts.
    criteria_considered: list[NonEmptyText] = []
    initiatives: list[InitiativeComparison] = Field(min_length=1)
    # Anything true of the comparison as a whole rather than one option.
    cross_cutting_notes: list[Claim] = []

    @model_validator(mode="after")
    def _one_entry_per_initiative(self) -> Comparison:
        ids = [i.initiative_id for i in self.initiatives]
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        if duplicates:
            raise ValueError(f"an initiative is compared more than once: {', '.join(duplicates)}")
        return self

    def compared_ids(self) -> set[str]:
        return {i.initiative_id for i in self.initiatives}
