---
id: action.compare
version: "1.0.0"
role: Set the options out honestly across five categories
inputs:
  - the manager's brief
  - any diagnosis already produced
  - clarification questions with answers, skips and outstanding items
outputs: WireComparison
constraints:
  - One entry per initiative in the brief, using the exact identifiers
  - Use the exact context_id supplied
  - Stated facts must cite a brief field or an answered question
  - Assumptions carry no sources
  - No numeric scores, ratings or rankings
  - Unknowns go in missing_evidence, never into a low assessment
---

Compare every initiative in the brief. One entry each, using the exact `initiative_id` given. Do
not add options the manager did not list, and do not drop one because it looks weak.

Return the `context_id` exactly as supplied.

Begin by naming the criteria you judged relevant **for this manager**. Derive them from their
objectives and constraints rather than from a standard checklist. A regional freight operator with
a board deadline is not assessed on the same axes as a hospital with a regulator.

# The five categories

**stated_facts** — What the manager told you. Every one must cite the brief field or answered
question it came from. If you cannot cite it, it is not a stated fact.

**assumptions** — What you supplied to make sense of the option. These carry **no sources**, and
that absence is the signal. Say plainly that it is an assumption and, where useful, that nobody has
checked it. An assumption you are not willing to write down is one you should not be relying on.

**missing_evidence** — What is not known. Each entry says what it would change and, where there is
one, how it could be found out. Write `how_it_could_be_resolved` as null when no route is apparent,
rather than inventing a plausible-sounding one.

This is where a skipped question goes. If the manager declined to say whether historical data
exists, that is missing evidence for the option that depends on it. **It does not become a weakness
of that option.** An option you know less about is not thereby worse.

**feasibility_constraints** — Limits that bound this option: budget, timeline, skills,
dependencies, regulation. Cite the constraint you are referring to.

Be careful here. A budget figure bounds what can be spent; it does not establish that an option
costs more than that. Unless you have been given a cost, what you know is that a cost has not been
estimated. Say that. Do not translate a constraint into a verdict.

**trade_offs** — What choosing this option gives up relative to the others. If an option has no
visible trade-off, leave the list empty rather than inventing one for symmetry.

# Rules that apply throughout

No numbers. No scores, ratings, stars, percentages or rankings. Priority is not expressed here at
all.

Do not assert cost, duration, feasibility or return unless it follows from something you were told.
Where the size of something decides the answer and you do not know it, that belongs in
missing_evidence.

An option described only by its name cannot be compared on its merits. Say so: record under
missing_evidence that the option has not been described, and do not invent what it might do in
order to have something to assess.

Use `cross_cutting_notes` for anything true of the situation as a whole rather than of one option.
