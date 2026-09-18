# Decision record

Each entry states the decision, why it was taken, and what was rejected. Superseded decisions are
kept with their replacement named, because the assessment is partly about how the design evolved.
Entries are not deleted.

**Status values:** Confirmed by the project owner. Proposed and awaiting review. Superseded. Open.

---

## D-001 — Implement the IoC method, not the BlueCallom platform

**Status:** Confirmed · 2026-09-18

We implement the principles stated on
<https://bluecallom.com/intelligence-over-code-method/> in our own stack. We do not imitate
GPTBlue Studio or borrow its component vocabulary.

**Why:** We have no access to the platform. Claiming to have used its internals would be a
fabrication, and an assessor from BlueCallom would see it immediately. A faithful implementation
of the stated principles is both honest and more defensible.

---

## D-002 — Runtime prompts as version-controlled files loaded at runtime

**Status:** Confirmed · 2026-09-18

Runtime prompts live in `backend/prompts/` as Markdown with front matter declaring identifier,
version, role, inputs, outputs and constraints. Python loads them from disk. No prompt text in a
Python string literal.

**Why:** The source page claims better models yield better responses "without needing to change a
single line of code." That claim is untestable if prompts are literals inside application logic.
Files on disk also make the prompts reviewable as the primary artefact, which is what the method
asserts they are, and put their evolution in Git history.

**Rejected:** Prompts in a Python module, which defeats the purpose. Prompts in a database, which
adds a dependency and hides how the intelligence evolved.

---

## D-003 — Comparison is qualitative and provenance-labelled. No weighted scoring in the MVP

**Status:** Confirmed · 2026-09-18 · **supersedes D-003a**

Each initiative is compared through five separately labelled categories: stated facts,
assumptions, missing evidence, feasibility constraints, and trade-offs. No numeric score, no
weights, no ranking arithmetic in the MVP.

**Why:** Directed by the project owner, and correct on the merits. A weighted score over partial
information manufactures false precision. Its specific failure is that an unknown has to become
some number, and whatever number is chosen, the option we know least about is silently penalised
or silently flattered. A manager cannot audit that, because the arithmetic hides the provenance
of every input.

The five-category structure keeps provenance visible instead: a recommendation resting on an
assumption has to say so. Each category is a distinct schema field, so a label cannot be lost in
transit.

**Rejected:** Weighted scoring in the MVP. If it returns later, it arrives with documented scales,
documented weights and a written statement of its limitations, never implicitly.

### D-003a — Superseded: "the model judges, Python counts"

**Status:** Superseded on 2026-09-18 by D-003.

The earlier design had the model assign per-criterion scores and weights, with Python computing
weighted totals, ranks and revision deltas. It was withdrawn at the project owner's direction
before any implementation. Recorded here because the reasoning behind its withdrawal is part of
the design argument, not because any code was written against it.

---

## D-004 — A bounded advisory loop, not a fixed pipeline

**Status:** Confirmed · 2026-09-18 · **supersedes D-004a**

Diagnosis, clarification, comparison, recommendation and revision are advisory responsibilities,
each with its own prompt and its own place in the interface. A prompt chooses which action is
appropriate given the session state. Code fixes the set of permitted actions and the limits on the
loop.

**Why:** The source page uses orchestration language without prescribing a sequence. Under the
method's hierarchy, deciding what to do next given a manager's situation is a judgement, and
judgements belong in prompts. A fixed order in Python would put the central process decision in
the subordinate, and would also produce bad advice: a well-specified brief does not need
clarification, and a vague one may need it more than once.

**Rejected:** A fixed five-step sequence. Also rejected: a single mega-prompt, which would be
cheaper and would make both the method and the revision delta invisible.

### D-004a — Superseded: the fixed five-stage pipeline

**Status:** Superseded on 2026-09-18 by D-004.

The original design ran diagnose, clarify, compare, recommend and revise in a fixed order, one
endpoint each. Corrected at the project owner's direction before implementation. No code was
written against it.

---

## D-005 — Code enforces schemas, limits, state integrity and action contracts

**Status:** Confirmed · 2026-09-18

Four controls sit in Python and cannot be waived by any prompt: schema validation of every model
response, execution limits on the advisory loop, append-only validated state transitions, and a
fixed contract of permitted actions.

**Why:** Directed by the project owner, and necessary. We verified that the BlueCallom source page
says nothing about validation, schemas, limits or control, so these are our engineering judgement
and the documentation says so rather than attributing them to the method.

They are compatible with the hierarchy because they decide nothing. No guard has an opinion about
which initiative is better. They are the "precision" case that the page reserves for code when it
states that IoC "has nothing to do with 'No-Code'."

**Rejected:** Pushing these controls into prompt text to reduce the Python line count. That would
be method theatre and would produce an application that cannot be trusted to terminate.

---

## D-006 — React with Vite and TypeScript

**Status:** Confirmed · 2026-09-18 · **amends D-006a**

**Why, on suitability:** Several coordinated panels over one evolving session object, updated
partially per advisory turn, is React's core competence.

**Why, on maintainability:** TypeScript makes the API contract explicit at the boundary most
likely to break silently. Every backend response is already a declared Pydantic contract;
mirroring it in TypeScript catches drift at compile time rather than during a demonstration.
Vite needs no build configuration and proxies the API, removing CORS from the developer's
concerns.

**On component libraries:** We start with plain CSS modules and design tokens because assessment
part 3 asks us to explain the UI/UX decisions, and a hand-built layout makes those decisions ours
to explain. This is a choice about the deliverable, not a methodological objection. Adopting a
headless library later for accessible dialogs, comboboxes or focus management would be an
improvement.

### D-006a — Corrected claim

The previous revision implied that TypeScript and component libraries sit awkwardly with
Intelligence-over-Code. That was wrong and the project owner corrected it. The method's hierarchy
concerns where business judgement lives, not the typing discipline or UI toolkit of the
presentation layer. Neither a type annotation nor a button component holds an opinion about which
initiative to fund.

---

## D-007 — Python with FastAPI

**Status:** Confirmed · 2026-09-18

**Why, on suitability:** Pydantic. Validating model output against a declared contract is the most
important code in an application of this kind, and FastAPI makes it the default path. The Python
SDK ecosystem for model providers is the most mature.

**Why, on maintainability:** Generated OpenAPI documentation describes the HTTP surface without a
separate document that drifts. Guards and validation are pure functions, unit testable with no
model and no network.

**Rejected:** A single Next.js application with API routes. It removes a process and a port, which
is genuinely tempting, but it moves prompt handling and schema validation into TypeScript and
blurs exactly the boundary this assessment examines.

---

## D-008 — One startup command via a root npm script

**Status:** Confirmed · 2026-09-18

After first-time setup, `npm run dev` from the repository root starts both processes through
`concurrently`.

**Why:** The brief asks for a simple documented startup command. The development machine is
Windows, where a Makefile would need extra tooling. A root npm script is cross-platform and costs
one dev dependency.

**Rejected:** A Makefile. Also rejected: parallel shell and PowerShell scripts that would need to
be kept in step.

---

## D-009 — Offline fixture mode, labelled, and never a fallback

**Status:** Confirmed · 2026-09-18

The model client can replay recorded fixtures instead of calling a provider. Two rules: the
interface labels fixture output as sample data, and a failed live call never silently becomes a
fixture response. Offline mode is entered by configuration, deliberately.

**Why:** A reviewer may have no API key, no budget or no network, and an application that cannot
be run cannot be assessed. The two rules exist because a demonstration that quietly substitutes
canned answers for a failed call is misleading about what the software actually does, which is a
worse failure than an error message.

**Rejected:** Requiring a live key. Also rejected, and never acceptable: shipping a key.

---

## D-010 — Fictional demonstration data only

**Status:** Confirmed · 2026-09-18

Fictional organisations, initiatives and budgets, labelled as sample data in the interface.

**Why:** Directed by the project owner, and correct regardless. Real employer data in a repository
intended for public review would be a confidentiality breach. Inventing plausible BlueCallom
customer data would be worse.

---

## D-011 — Development prompts and runtime prompts are separate artefacts

**Status:** Confirmed · 2026-09-18

`docs/prompts/` records the instructions that produced the software, verbatim and in order.
`backend/prompts/` holds the prompts the software executes.

**Why:** The assessment asks separately for a working application and for an account of how it was
built. Merging the two would obscure which prompts a user of the application is actually subject
to.

---

## D-012 — This application covers assessment parts 2 and 3 only

**Status:** Confirmed · 2026-09-18

The repository addresses building the application and designing its interface. The candidate's
prior professional work is presented separately by the project owner.

**Why:** Directed by the project owner. This application was built for the assessment, starting
2026-09-18, and its Git history says so. Presenting newly written code as evidence of earlier
professional experience would misrepresent the candidate's record, which is a far more serious
problem than any technical shortcoming in the code.

---

## D-013 — Record AI assistance accurately

**Status:** Confirmed · 2026-09-18

The repository states that ChatGPT supported requirements analysis and development-prompt
preparation, and that Claude performs implementation under the project owner's direction. No
document implies that every line was typed by hand.

**Why:** Directed by the project owner, and it is the honest description of how this repository is
produced. In an assessment about AI-assisted development, misrepresenting the process would
undermine the submission more than the assistance ever could.

---

## D-014 — Runtime model provider deliberately left open

**Status:** Open · 2026-09-18

The provider choice is deferred until available API access is confirmed. The model client is
defined as an interface with adapters behind it.

**Why:** Directed by the project owner. The decision affects one module. Deferring it blocks
nothing in the skeleton, the guards, the schemas or the interface, and committing early to a
provider we may not have credentials for would be the more expensive mistake.

---

## Decisions still open

D-014 provider, plus session persistence, export formats, test depth and streaming. Tabulated with
recommendations in [requirements.md](requirements.md), section D-b.
