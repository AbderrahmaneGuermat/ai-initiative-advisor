# Requirements

Status: **application implemented; documentation current as of prompt
[016](prompts/016-submission-documentation.md).** The advisory flow, runtime prompts, validation
boundary and interface are built and tested. Revision after a constraint change, offline replay,
export and persistence are not implemented; each is marked where it appears below.

Earlier revisions of this file described the project before any application logic existed. Their
proposals are kept here where they still explain a decision, and are labelled **proposed, not
implemented** where they were never built. The history of each change is in
[worklog.md](worklog.md) and [decisions.md](decisions.md).

This file separates three kinds of statement, because conflating them is the easiest way to fail an
assessment of this type:

- **A — What the assessment asks for.** Taken from the assignment as relayed by the project owner.
- **B — What BlueCallom states about Intelligence-over-Code.** Quoted from BlueCallom's own page,
  with the source named.
- **C — Our interpretation and implementation choices.** Everything else. These are ours to
  defend, and ours to change.

---

## A. Assessment scope

The assessment has three parts. **This application addresses parts 2 and 3.**

| # | Part | Addressed by |
|---|---|---|
| 1 | Present one application the candidate built previously | **Not this repository.** Supplied separately by the project owner |
| 2 | Build a strategy-consulting application for managers using the IoC method | This repository |
| 3 | Design a sample enterprise AI interface and explain the UI/UX decisions | This repository, through the same application, with the rationale in [ui-ux.md](ui-ux.md) |

**This application was newly built for the assessment and is not evidence of prior professional
work.** Its Git history begins on 2026-09-18 and shows exactly that.

### A2 expanded — what the application was asked to do

Agreed in [prompts/001-project-brief.md](prompts/001-project-brief.md) and refined in
[prompts/002-design-review-and-skeleton.md](prompts/002-design-review-and-skeleton.md): help a
manager prioritise candidate enterprise AI initiatives against their objectives, resources and
constraints.

| Requirement | Status |
|---|---|
| 1. Ask relevant clarification questions rather than answering a vague brief | **Implemented.** Up to three per round, chosen by the clarify prompt |
| 2. Compare alternatives | **Implemented.** Qualitative, five labelled categories per option |
| 3. Give a justified recommendation | **Implemented.** Stance, rationale, conditions, risks, first actions, open unknowns and a confidence note |
| 4. Revise its advice when constraints change | **Not implemented as a flow.** The `Revision` contract exists and is validated, but no prompt, action or interface produces one. A changed brief requires a new advisory session; see C2 |

---

## B. What BlueCallom states about Intelligence-over-Code

Single source, first retrieved on 2026-09-18 and rechecked on 2026-09-19:
**<https://bluecallom.com/intelligence-over-code-method/>**

Quoted phrases are BlueCallom's wording from that page. Our reading of them is section C and is
never mixed in here.

### B1. The core hierarchy

**"Prompt is King"** and **"Code is a subordinate of the King."** The page describes prompts as
"the language with the Intelligence in AI, not stiff and linear code", and IoC as prioritising "the
hierarchical value and importance of a prompt over any code".

### B2. What code is for

Code serves "API Access, Deep Learning algorithms, numerical processing, sending specific data to
a database", with such functions "triggered by a prompt". The page's guidance adds that
"Functions will not call the LLM but code that can't be created with prompts like API access,
algorithms, reinforced learning functions etc."

### B3. IoC is not no-code

**"IoC has nothing to do with 'No-Code'; we do use code whenever it is an advantage."**

### B4. Claimed benefits

"With better models, we get better responses without needing to change a single line of code",
and with updated context "a prompt can elicit deeper responses without requiring any code
changes".

### B5. Prompt-structure guidance

The page publishes a reminder prompt to give ChatGPT when designing an agent. It asks for each
prompt to state:

- "Role of the agent: What the agent is responsible for"
- "Inputs required: The data or parameters the agent needs"
- "Expected outputs: The result the agent should produce"
- "Special instructions or constraints: Any specific rules or guidelines"

and says "Prompts should be modular, reusable, and task-specific".

### B6. The published procedure

Three steps: tell ChatGPT which agent you want to build, using the reminder prompt; ChatGPT
returns "a solution description, the prompts that you would need", and Python code for complex
algorithms or API access; then "copy all the prompts into the GPTBlue Studio", create the agent
there, and optionally upload code to the AgenticBlue platform or share it for "an isolated test".

### B7. What the page does not state

- Nothing about validation, schemas, testing frameworks, execution limits, state management or
  security, beyond the isolated test of submitted code mentioned in B6.
- No file format for prompts, no required model vendor, and no reference architecture for an
  implementation outside BlueCallom's own platform.

Everything this repository does about schema enforcement, execution limits and state integrity is
therefore **our engineering choice, not a BlueCallom requirement**, and is labelled as such in C4.

### B8. Platform features we do not use

The published procedure ends in GPTBlue Studio and the AgenticBlue platform. **We have no access to
either and do not integrate with them.** This is a standalone application that follows the
method's principles and prompt structure; it does not reproduce the platform, and it does not
borrow the platform's product vocabulary for its own components.

---

## C. Our interpretation and implementation choices

### C1. Product framing

A single-purpose advisor, not a general chatbot. The manager brings a portfolio of candidate AI
initiatives and their constraints, and receives a justified, comparative recommendation with its
uncertainty kept visible. **Product name: AI Initiative Advisor.**

### C2. Advisory actions, not a fixed pipeline

Diagnosis, clarification, comparison and recommendation are **advisory responsibilities**, each with
its own prompt. A selector prompt chooses which one to perform next from the actions code currently
permits. A well-specified brief may go straight to comparison; a vague one is asked questions
first; a brief too thin to work with gets a request for context.

This is our reading of B1: deciding *what to do next* is judgement, so it belongs in a prompt.

**Revision was part of the original design and is not implemented.** The `revise` action and the
`Revision` contract exist in code and are validated in tests, but the action is deliberately
withheld from the selector, there is no revise prompt, and the interface has no revision flow. If
the manager changes the brief after a session, the interface withdraws the previous advice and asks
for a new session, started explicitly (see [ui-ux.md](ui-ux.md), section 7).

### C3. What prompts own

The runtime prompts in `backend/prompts/` own:

- Which advisory action to take next, and why (`actions/next-action.md`).
- What is missing, contradictory or assumed in the brief (`actions/diagnose.md`).
- Which clarification questions are decision-critical (`actions/clarify.md`).
- Which criteria matter, and how each option looks against them (`actions/compare.md`).
- What to recommend, in what order, and how to justify it (`actions/recommend.md`).

Each prompt carries front matter with its identifier, version, role, inputs, outputs and
constraints, which follows the structure BlueCallom's reminder prompt asks for (B5).

### C4. What code owns, and why this is not a violation

Code enforces the following. The model cannot waive them.

| Control | Enforced by code |
|---|---|
| **Schema** | Every model response is parsed into a declared contract. Invalid output is repaired once, then surfaced as an error. Never rendered unvalidated. |
| **Execution limits** | Maximum advisory actions and model requests per turn, per-request timeouts, a turn deadline and a maximum input size. |
| **State integrity** | Session state changes only through validated transitions. The manager's answers are written by one code path no model output reaches. Superseded results are kept and labelled, not shown as current. |
| **Action contract** | The selector may only choose from the actions code currently permits. |

**This is our interpretation, not a BlueCallom instruction.** B7 records that the page says nothing
about these. We consider them compatible with the method because they decide nothing about which
initiative is better, and B3 explicitly allows code "whenever it is an advantage".

### C5. Comparison is qualitative and explained, not scored

No weighted numerical scoring. Each initiative is set out across five separately labelled
categories:

| Category | Meaning |
|---|---|
| **Stated facts** | What the manager told us, citing the brief field or answered question |
| **Assumptions** | What the advisor assumed in order to proceed, carrying no sources |
| **Missing evidence** | What is not known and would change the assessment |
| **Feasibility constraints** | Budget, timeline, skills, dependencies and regulatory limits |
| **Trade-offs** | What choosing this option gives up |

Separate fields and resolvable references make the advice auditable. They do not make it correct:
a schema cannot tell a fact from an assumption filed as one, and a reference check confirms only
that the cited identifier exists (decision D-016). **An unknown is never converted into a zero, a
low score or a neutral midpoint.**

### C6. Clarification behaviour

- At most three questions per round, each stating what its answer would change.
- The manager may answer, explicitly skip, or leave a question blank.
- Skipped and unanswered questions stay visible in the interface as open unknowns, are listed in
  the recommendation, and are never cited as sources. (An earlier revision also mentioned an
  exported brief; export is not implemented.)

### C7. Fictional demonstration data

One fictional organisation, Larkfield Regional Freight, in
`backend/app/data/scenarios/larkfield-freight.json`. No employer data, no real operational data, no
BlueCallom platform access, no customer material.

### C8. Offline fixture mode — proposed, not implemented

The original plan was a mode that replays recorded responses so the application could be reviewed
without a key, labelled as sample data and never used as a fallback for a failed live call. **It
was not built.** The `OFFLINE_FIXTURE_MODE` setting is read but does nothing, and
`backend/fixtures/` is empty. The second rule still holds in the code that exists: a failed live
call surfaces as a failure and is never replaced by stored output.

Browser screenshots taken during development from recorded or prepared session payloads were
review tooling outside the repository. They are not an offline mode of the product.

### C9. Acceptance criteria

| Criterion | Status |
|---|---|
| 1. Changing a prompt file changes the advice, with no Python edit | **Mechanism tested:** prompts are read from disk on every call, and a test shows an edit reaching the provider adapter without a restart. Not demonstrated with a live before-and-after comparison |
| 2. Changing one constraint produces a revision naming what moved and why | **Not met.** No revision flow; see C2 |
| 3. Every recommendation is traceable to the five categories, with assumptions labelled | **Met structurally**, with the limits stated in C5 |
| 4. The application asks rather than guesses, and never converts an unknown into a value | **Met** in the contracts and prompts, and observed in the recorded live runs |
| 5. Invalid output is repaired once, then surfaced, never silently rendered | **Met, tested** |
| 6. Execution limits hold even when a prompt requests further action | **Met, tested** |

---

## D. Decisions

### D-a. Confirmed

| Decision | Setting | Record |
|---|---|---|
| Interface and documentation language | English | — |
| Product name | AI Initiative Advisor | — |
| Frontend | React, Vite, TypeScript | D-006 |
| Backend | Python, FastAPI | D-007 |
| Model provider | OpenAI, Responses API with structured outputs; default model `gpt-5-mini` | D-019, closes D-014 |
| Numerical scoring | None | D-003 |
| Clarification questions per round | At most three | — |
| Session storage | In memory; lost when the backend restarts | D-023 |
| Reopening a session | By URL, while the backend still holds it; recovery, not persistence | D-044 |
| Deployment | Local execution only. No hosting, no Docker | — |

### D-b. Proposed earlier and not implemented

| Proposal | Outcome |
|---|---|
| Offline fixture mode, labelled as sample data | Not implemented (C8) |
| Revision after a constraint change | Contract only; no flow (C2) |
| Session persistence to a JSON file | Not implemented; sessions are in memory |
| Export as Markdown and JSON | Not implemented |
| One end-to-end test against fixtures | Not implemented. Tests use deterministic test doubles instead of a model |
| Response streaming | Not implemented, by choice |

---

## E. Out of scope

Hosting and deployment, Docker, authentication, multi-tenancy, a database, PDF export, integration
with GPTBlue Studio or any BlueCallom API, multi-agent parallelism, cross-session memory, and
languages other than English.
