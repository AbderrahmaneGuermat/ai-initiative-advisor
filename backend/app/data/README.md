# Sample data

## What these files are

**Manually authored fictional examples.** Every file in `scenarios/` and `examples/` was written by
hand to exercise the data contracts in `backend/app/models/`.

## What these files are not

- **Not recorded model responses.** No model produced any of this text.
- **Not evidence that the advisor works.** They were written before the model integration existed,
  to fix the *shape* advisory output must take and to show that the contracts accept a realistic
  example and reject a malformed one. The advisor now generates real output; evidence of how it
  behaves is in the live runs recorded in `docs/worklog.md`, not here.
- **Not fixtures for an offline mode.** Offline replay is not implemented, and
  `backend/fixtures/` is an empty placeholder. If replay is ever built, its output must be labelled
  as sample data and never substituted for a failed live call. See `docs/decisions.md`, D-009.
- **Not the brief used live as-is.** `scenarios/larkfield-freight.json` is the sample brief the
  interface loads. Its headcount constraint is deliberately empty; the coherent live demonstration
  filled it in through the interface before starting.
- **Not real.** Larkfield Regional Freight does not exist. The organisation, its staff numbers, its
  customers, its budget and its initiatives are invented. No employer data and no real operational
  data appears anywhere in this repository.

## Contents

| File | Contract | Shows |
|---|---|---|
| `scenarios/larkfield-freight.json` | `ManagerBrief` | A deliberately incomplete brief: an objective with no rationale, a constraint with a named kind and no value, an initiative with no description |
| `examples/01-clarification-round.json` | `ClarificationRound` | Three questions, the maximum permitted in one batch, with one answered, one explicitly skipped and one untouched |
| `examples/02-comparison.json` | `Comparison` | Three initiatives across the five categories, with unknowns recorded as unknowns rather than as low values |
| `examples/03-recommendation.json` | `Recommendation` | A justified shortlist carrying its open unknowns and the assumptions it rests on |
| `examples/04-revision.json` | `Revision` | The budget is cut; one initiative moves, two hold, and the explanation says which and why. The contract is validated, but the application has no revision flow |

The examples run in sequence against the same scenario, so they can be read as one worked case.

## What validating them proves

That the payloads match the declared shapes, and that every identifier they cite exists in the
brief or in an answered clarification question.

It does not prove that the analysis is sound, that a claim filed under stated facts is a fact, or
that a cited input supports the claim citing it. A schema cannot establish any of that. See
`docs/decisions.md`, D-016.
