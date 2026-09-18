# Worklog

A factual record of work done, checks performed and issues left open. Entries are appended, never
rewritten. Nothing is recorded here that did not actually happen.

---

## 2026-09-18 — Prompt [001](prompts/001-project-brief.md), project brief

**Instruction:** Organise the repository, document requirements, propose an implementation plan.
Do not implement the application. Review BlueCallom's Intelligence-over-Code method first.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

### Work completed

1. Inspected the working directory. It was empty and was not a Git repository. Nothing existed to
   preserve.
2. Initialised a Git repository.
3. Reviewed BlueCallom's published material on the method:
   - <https://bluecallom.com/intelligence-over-code-method/> — retrieved successfully. Source of
     the "Prompt is King" hierarchy and the stated division between prompts and code.
   - <https://bluecallom.com/new-agentic-ai-framework/> — retrieved successfully. Source of the
     three-to-twenty prompts per agent figure, the Agentic Spin, and Human Interaction Points.
   - A web search was used to locate additional pages and to corroborate the statement that IoC
     is not no-code.
4. Created the documentation set: `README.md`, `docs/requirements.md`, `docs/architecture.md`,
   `docs/decisions.md`, `docs/worklog.md`, `docs/prompts/`.
5. Saved the project brief verbatim as
   [docs/prompts/001-project-brief.md](prompts/001-project-brief.md).
6. Added `.gitignore` covering Python, Node and environment files, so that `.env` cannot be
   committed once it exists.
7. Made the initial commit.

### Checks performed

- Confirmed the working directory was empty before initialising Git, so no existing work was at
  risk.
- Confirmed the saved brief in prompt 001 matches the instruction as received, with only a
  metadata header added above a horizontal rule.
- Confirmed every claim attributed to BlueCallom in `docs/requirements.md` section B traces to a
  page that was actually retrieved in this session, and recorded the source URL beside it.
- Confirmed `.gitignore` excludes `.env` and both dependency directories before committing.

No tests were run and no application code was written, because none exists. No functional
verification of any kind has taken place.

### Issues and observations

1. **One source page was unavailable.** `https://bluecallom.com/prompt-over-code-method/` returned
   HTTP 404 on direct retrieval, although it appears in search results under that URL. Its content
   was corroborated through search result extracts rather than direct retrieval. The material
   sourced this way is the "not no-code" statement in requirements B4. It is flagged here rather
   than presented as a verified direct quotation from a page we loaded.
2. **BlueCallom does not publish a development lifecycle.** The public pages give a philosophy and
   a component vocabulary, not a procedure, a prompt file format or a reference architecture.
   Everything at that level in this repository is our own choice and is labelled as such in
   requirements section C. This is stated so that no one later mistakes our conventions for
   BlueCallom's requirements.
3. **Eight decisions are open** and block the start of implementation. They are tabulated as D1
   to D8 in [requirements.md](requirements.md), section D. The two that most affect the shape of
   the code are D1, the model provider, and D4, offline mode.
4. **A design risk is recorded, not yet mitigated.** The characteristic failure of an
   Intelligence-over-Code project is a codebase that claims prompt primacy while business rules
   accumulate in Python conditionals. Acceptance criterion C7.1 exists as the test for this, and
   it cannot be exercised until code exists.
5. **Latency and cost are unestimated.** Five sequential model calls per session may be too slow
   for a comfortable demonstration. This will be measured once the pipeline runs. It has not been
   guessed at in the architecture document.

### Status at end of entry

Design documented. Implementation not started, as instructed. Awaiting the project owner's review
of the plan and answers to the open decisions.

---

## 2026-09-18 — Prompt [002](prompts/002-design-review-and-skeleton.md), design review and skeleton

**Instruction:** Correct the design documentation on six points, then implement the project
skeleton only. Verify what can be verified and report what cannot.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

This entry is written in two parts, because the instruction asked for two separate commits.

### Part A — documentation corrections

1. Re-retrieved <https://bluecallom.com/intelligence-over-code-method/> and queried it
   specifically for statements about prompts, code, no-code, orchestration, control mechanisms and
   claimed benefits.
2. Rewrote `docs/requirements.md`:
   - Assessment scope restated. This repository addresses parts 2 and 3 only. Part 1 is the
     project owner's prior professional work and is handled separately. Added an explicit
     statement that this application is newly built and is not evidence of earlier work.
   - Section B now cites the single working source URL throughout.
   - Replaced the fixed five-stage pipeline with advisory actions chosen per turn.
   - Added the code-enforced controls, labelled as our engineering judgement.
   - Replaced weighted scoring with the five-category qualitative comparison.
   - Added the maximum of three clarification questions and the rule that skipped answers stay
     visible as unknowns or labelled assumptions.
   - Recorded the confirmed choices and the decisions that remain open.
3. Rewrote `docs/architecture.md`: bounded advisory loop with a fixed action contract, the four
   guards, the comparison model with no numeric default path, and technology rationale restated on
   suitability and maintainability.
4. Rewrote `docs/decisions.md`: superseded entries kept with their replacements named, rather than
   deleted.
5. Rewrote `README.md`: scope, status, and a short account of the method.
6. Saved prompt 002 verbatim and added it to the prompt index.

### Checks performed, Part A

- Confirmed every statement attributed to BlueCallom in requirements section B comes from the
  single page retrieved in this session, and that the page was reachable at the time of writing.
- **Correction to the previous entry.** The 2026-09-18 entry for prompt 001 recorded that the
  "not no-code" statement had been corroborated only through search extracts, because
  `bluecallom.com/prompt-over-code-method/` returned HTTP 404. On re-checking, that statement
  appears on the working method page itself, and it is now quoted and cited from there. The
  earlier entry is left unedited, as the worklog is append-only. The 404 page is no longer cited
  anywhere in the documentation.
- **Verified a negative and recorded it.** The source page makes no mention of testing,
  validation, schemas, execution limits or control mechanisms. This is stated in requirements B7,
  so that the controls this project adds are not mistaken for BlueCallom requirements.
- Confirmed no document presents the application as prior professional experience.
- Confirmed the previous claim that TypeScript or a component library conflicts with IoC has been
  withdrawn and corrected, in architecture section 6 and decision D-006a.

### Issues, Part A

1. The revised design has not been validated against running advisory code, because none exists.
   In particular the claim that a bounded adaptive loop is workable within acceptable latency is
   untested.
2. Five decisions remain open: model provider, session persistence, export formats, test depth and
   streaming. Only the provider was explicitly deferred by the project owner; the other four carry
   recommendations awaiting a decision.
