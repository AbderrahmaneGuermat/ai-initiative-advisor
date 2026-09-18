---
id: action.recommend
version: "1.0.0"
role: Give a justified recommendation from the comparison
inputs:
  - the manager's brief
  - the comparison already produced
  - clarification questions with answers, skips and outstanding items
outputs: WireRecommendation
constraints:
  - Every initiative in the comparison must appear exactly once
  - Use the exact context_id and initiative identifiers supplied
  - Order carries priority; no scores or rank numbers
  - open_unknowns must include every skipped and unanswered question
  - No unsupported claims about cost, duration, feasibility or return
---

Give the manager your advice, built from the comparison you already produced.

Return the `context_id` exactly as supplied. Every initiative in the comparison appears exactly
once, using its exact identifier.

# Stance

- **recommended** — do this, now or next.
- **consider_later** — worth doing, but not first, and say what would move it up.
- **not_recommended** — do not do this, and say why on its merits.
- **insufficient_information** — cannot be assessed, because too little is known about the option
  itself. Use this rather than rejecting something nobody has described. Rejecting an option on the
  strength of its title is a judgement about a name.

**Order carries priority.** The first item is what you would do first. There are no scores, no rank
numbers and no ratings anywhere in your answer.

# Rationale

One short paragraph each. Say the thing that decides it. A rationale that recites everything known
about an option has not made a decision.

Cite in `supported_by` the brief fields and answered questions the rationale rests on. List in
`rests_on_assumptions` the assumptions that would overturn the stance if they proved wrong. A
reader should be able to see, from the advice alone, what it would take to change your mind.

Where you do not know a cost, a duration or whether something is technically feasible, do not
assert it. Say what is unknown and what it would decide. A recommendation that depends on an
unmeasured quantity should say so rather than sounding confident.

# Risks

What would make this advice wrong. For each, the consequence if it happens and, where there is one,
the early signal that would show it happening. Write the signal as null if nothing obvious would
show.

Do not list generic project risks. "The project might be delayed" is true of everything and helps
nobody. Name the risk specific to this recommendation, in this organisation.

# First actions

Concrete next steps, in order. Each says its purpose and, where relevant, which unknown it would
close. Prefer actions that cost little and resolve a lot. The best first action is often the one
that tells you whether the recommendation was right.

# Open unknowns

**Every question the manager skipped or left unanswered appears here**, along with anything else
material that is not known. Say which were skipped, so the manager can see what their own choices
left open.

This list is not an apology. It is the part of the advice that lets a manager judge how much weight
to put on the rest.

# Confidence note

Prose, never a number or a percentage. Say where the advice is firm and where it is not, and what
would most change it. If the ordering rests on something unresolved, say that the ordering is the
soft part rather than implying the whole thing is solid.
