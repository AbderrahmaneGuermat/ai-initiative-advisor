# Prompt 004 — Data Contracts and Foundations

- **Date received:** 2026-09-18
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)

The text below is the instruction exactly as received.

---

Continue from the published repository after reviewing its current state.

Save this instruction verbatim as `docs/prompts/004-data-contracts-and-foundations.md` before making changes, and update the prompt index.

This iteration covers configuration consistency, data contracts and one fictional example. Keep it small and reviewable.

1. CORRECT THE EXISTING INCONSISTENCIES

* `.env.example` advertises BACKEND_HOST and BACKEND_PORT, but `scripts/dev-backend.mjs` always uses 127.0.0.1:8000. For this MVP, retain the fixed local addresses and remove the unused configuration fields. Make the documentation match actual behaviour.
* Describe the IPv6 behaviour as observed on the tested Windows machine, not as a universal Vite behaviour. Keep platform support distinguished from platforms actually tested.
* Correct claims that schema validation prevents assumptions from being presented as facts. Schemas enforce structure; valid source references improve traceability; neither proves factual correctness.
* Resolve the mismatch between the planned diagnosis prompt and the permitted-action table. Document an explicit mapping between actions and their outputs.
* Remove the remaining claim that Next.js or TypeScript inherently blurs the IoC boundary. Explain our stack through suitability and familiarity.

Preserve historical development prompts. Corrections belong in current documentation and new decision entries.

2. IMPLEMENT THE DATA CONTRACTS

Add Pydantic contracts under `backend/app/models/` for:

* The manager's brief: objectives, constraints and candidate initiatives with stable identifiers.
* Clarification questions and responses, distinguishing answered, unanswered and explicitly skipped questions. At most three questions per batch.
* Qualitative comparisons with separate fields for stated facts, assumptions, missing evidence, feasibility constraints and trade-offs.
* Recommendations referencing known initiatives, with supporting information, risks and first actions.
* Revisions identifying the previous and current context and explaining changes.
* The next-action response, restricted to the documented permitted actions.

Keep missing values explicit. Do not introduce numerical scores or silently fill unknowns with defaults.

Use lightweight source references to supplied brief fields or clarification answers where claims rely on user input. Validate referenced identifiers where appropriate. Do not claim these checks establish semantic truth.

3. ADD ONE FICTIONAL WORKED EXAMPLE

Create one sample scenario with three candidate initiatives and an incomplete brief.

Provide sample payloads demonstrating clarification, a skipped answer, comparison, recommendation and a revision after a constraint changes. Validate them against the contracts.

Label these as manually authored fictional examples, not recorded model responses. They must not imply that model integration or advisory execution already exists.

4. VERIFY AND DOCUMENT

Add focused tests for the important contract boundaries: unknown actions, excessive clarification questions, invalid references, and preservation of unanswered or skipped information. Validate the example payloads.

Keep business judgement out of validators. Do not implement model calls, the advisory loop, persistence, exports or a frontend redesign in this iteration.

Record actual checks and remaining limitations in the worklog. Keep the README clear about which capabilities are implemented versus merely specified.

Commit the changes and push to the already confirmed repository after checking that origin still points to:
https://github.com/AbderrahmaneGuermat/ai-initiative-advisor.git

Return a concise summary, changed files, test results and the published commit hash. Then stop for review.
