# Decision record

Each entry states the decision, why it was taken, what was rejected, and its current status.
Decisions marked **Proposed** are not settled and are listed for review. Decisions marked
**Open** are waiting on the project owner and appear as D1 to D8 in
[requirements.md](requirements.md).

Nothing here has been validated against running code, because no code exists yet.

---

## D-001 — Implement the IoC method, not the BlueCallom platform

**Status:** Proposed
**Date:** 2026-09-18

The assessment asks for an application built according to Intelligence-over-Code. BlueCallom's
own solutions are assembled in GPTBlue Studio, which we do not have access to. We therefore
implement the method's principles in our own stack and say so explicitly, rather than imitating
platform vocabulary we cannot honour.

**Why:** Claiming to have used the Agentic Spin or the synaptic connector protocol without the
platform would be a fabrication, and an assessor from BlueCallom would spot it immediately. A
faithful implementation of the stated principles is both honest and more defensible.

**Rejected:** Mimicking GPTBlue's component names in a local codebase.

---

## D-002 — Prompts as version-controlled files, loaded at runtime

**Status:** Proposed
**Date:** 2026-09-18

Runtime prompts live in `backend/prompts/` as Markdown files with YAML front matter declaring
identifier, version, role, inputs, outputs and constraints. Python loads them from disk. No prompt
text is embedded in a Python string literal.

**Why:** BlueCallom states that prompts are modular and reusable with defined roles, inputs,
outputs and constraints, and claims that behaviour improves without code changes. Neither claim
survives if the prompts are string literals inside application logic. Files on disk also make the
prompts reviewable as the primary artefact, which is what the method asserts they are.

**Rejected:** Prompts in a Python module, and prompts in a database. The first defeats the
purpose. The second adds a dependency and removes the Git history of how the intelligence
evolved, which is itself part of the deliverable.

---

## D-003 — The model judges, Python counts

**Status:** Proposed
**Date:** 2026-09-18

The model assigns criteria, weights and per-initiative scores with written reasoning. Python
performs the weighted arithmetic, the ranking and the revision delta. Python contains no rule
about what makes an initiative good.

**Why:** This is BlueCallom's stated boundary, which places numerical processing in code while
insisting that code is "never intelligent, autonomous, or reasoned about." It also produces
better software. Language models are unreliable arithmetic engines, and a ranking computed in
Python is reproducible, testable and explainable to a manager who asks why something moved.

**Rejected:** Asking the model for a final ranked list directly. It is less reproducible, and it
makes the revision delta impossible to compute exactly.

---

## D-004 — Five prompt stages, sequential, with two human checkpoints

**Status:** Proposed
**Date:** 2026-09-18

Diagnose, clarify, compare, recommend, revise. The manager intervenes after clarify and after
recommend.

**Why:** These map one-to-one onto the four behaviours the brief requires, plus the diagnosis
step that makes clarification targeted rather than generic. The count sits inside BlueCallom's
stated range of three to twenty prompts per agent. The two checkpoints mirror BlueCallom's Human
Interaction Points at a scale we can actually implement.

**Rejected:** A single mega-prompt. It would be faster and cheaper, and it would make the method
invisible. It also cannot support a revision that explains what changed, because there is no
retained intermediate state to compare against.

---

## D-005 — React with Vite and TypeScript for the interface

**Status:** Proposed, matches the brief's suggestion
**Date:** 2026-09-18

**Why:** The interface is three coordinated panels over one session object, which is React's
core competence. Vite needs no build configuration. TypeScript catches API contract drift, which
is the most likely source of silent breakage across a two-process split.

**Rejected:** Svelte and plain HTML with htmx, both defensible and both less legible to an
assessor expecting mainstream enterprise tooling. A component library such as Material UI was
also rejected, because the assessment asks us to justify UI decisions and a library would mean
justifying someone else's.

---

## D-006 — Python with FastAPI for the backend

**Status:** Proposed, matches the brief's suggestion
**Date:** 2026-09-18

**Why:** Pydantic. Validating model output against a declared schema is the most important code
in an IoC application, and FastAPI makes that the default path rather than an add-on. The Python
SDK ecosystem for model providers is the most mature, and OpenAPI documentation comes free.

**Rejected:** A single Next.js application with API routes. It removes a process and a port,
which is genuinely tempting, but it would put prompt handling and schema validation in
TypeScript and blur exactly the boundary the assessment is testing. The full reasoning is in
[architecture.md](architecture.md), section 5.

---

## D-007 — One startup command via a root npm script

**Status:** Proposed
**Date:** 2026-09-18

After first-time setup, `npm run dev` from the repository root starts both processes through
`concurrently`.

**Why:** The brief asks for a simple documented startup command. The development machine is
Windows, and a Makefile would not run there without extra tooling. A root npm script is
cross-platform and needs one dependency.

**Rejected:** A Makefile, and separate shell and PowerShell scripts that would then need to be
kept in step.

---

## D-008 — Offline fixture mode

**Status:** Proposed, overlaps open decision D4
**Date:** 2026-09-18

The model adapter supports a mode that replays recorded responses from `backend/fixtures/`
instead of calling a provider.

**Why:** An assessor may review the repository without an API key, without budget, or without
network access. An application that cannot be run is an application that cannot be assessed. It
also makes the deterministic parts testable in continuous integration without spending money.

**Rejected:** Requiring a live key. Also rejected: shipping a key, which is never acceptable.

---

## D-009 — Fictional demonstration data only

**Status:** Proposed
**Date:** 2026-09-18

Three invented organisations with invented initiatives and budgets.

**Why:** Instructed by the project owner, and correct regardless. Real employer data in a public
assessment repository would be a confidentiality problem, and inventing plausible BlueCallom
customer data would be worse.

---

## D-010 — Development prompts and runtime prompts are separate artefacts

**Status:** Proposed
**Date:** 2026-09-18

`docs/prompts/` records the instructions that produced the software, in order, verbatim.
`backend/prompts/` contains the prompts the software executes. Neither directory references the
other as if they were the same kind of thing.

**Why:** The assessment asks separately for a working application and an explanation of the
prompts used to develop it. Merging the two would make both harder to read and would obscure
which prompts a user of the application is actually subject to.

---

## D-011 — Record AI assistance accurately

**Status:** Proposed
**Date:** 2026-09-18

The repository states plainly that ChatGPT supported requirements analysis and the preparation of
development prompts, and that Claude performs implementation under the project owner's direction.
No document will imply that every line was typed by hand.

**Why:** Instructed by the project owner, and it is the honest description of how this repository
is being produced. For an assessment about AI-assisted development, misrepresenting the process
would undermine the submission more than the assistance ever could.

---

## Decisions deferred to the project owner

D1 model provider, D2 product name, D3 interface language, D4 offline mode, D5 persistence,
D6 export formats, D7 test depth, D8 streaming. Each is tabulated with a recommendation in
[requirements.md](requirements.md), section D.
