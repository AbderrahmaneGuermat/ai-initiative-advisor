# Architecture

Status: **first advisory flow working.** OpenAI integration, runtime prompts, the bounded loop and the validation boundary are implemented and tested against deterministic doubles. Revision is validated but not offered; persistence, exports and offline replay are not implemented.
Revised following the design review in [prompts/002-design-review-and-skeleton.md](prompts/002-design-review-and-skeleton.md).

The organising constraint is BlueCallom's stated hierarchy, that the prompt carries the
intelligence and code carries the mechanics. See [requirements.md](requirements.md), sections B1
to B4. The architecture below exists to make that separation visible and auditable rather than
merely claimed, while keeping the controls that make the application safe to run.

---

## 1. Shape of the system

Two processes, one HTTP boundary.

```
┌─────────────────────────────┐        ┌──────────────────────────────────────────┐
│  React + Vite  (port 5173)  │        │  FastAPI  (port 8000)                    │
│                             │  JSON  │                                          │
│  Context panel              │ ─────► │  ┌────────────────────────────────────┐  │
│  Advisory thread            │ ◄───── │  │ Advisory loop (bounded)            │  │
│  Comparison + recommendation│  proxy │  │  asks the prompt what to do next,  │  │
│                             │  /api  │  │  enforces what is permitted        │  │
└─────────────────────────────┘        │  └──────┬──────────────────┬──────────┘  │
                                       │         │                  │             │
                                       │  ┌──────▼───────┐   ┌──────▼──────────┐  │
                                       │  │ prompts/*.md │   │ GUARDS          │  │
                                       │  │ decide       │   │ schema          │  │
                                       │  │  next action │   │ limits          │  │
                                       │  │  questions   │   │ state integrity │  │
                                       │  │  comparison  │   │ action contract │  │
                                       │  │  advice      │   └─────────────────┘  │
                                       │  └──────┬───────┘                        │
                                       │  ┌──────▼───────┐  ┌──────────────────┐  │
                                       │  │ model client │  │ session store    │  │
                                       │  └──────┬───────┘  │ export renderer  │  │
                                       └─────────┼──────────┴──────────────────┘  │
                                                 ▼ provider API  (or labelled fixtures)
```

The property that matters: the boxes containing business judgement are Markdown files. A
reviewer can read what the application thinks by reading `backend/prompts/`, without reading
Python. The boxes containing enforcement are Python, and the model cannot talk its way past them.

---

## 2. Orchestration: a bounded advisory loop

**There is no fixed five-step pipeline.** Corrected at the project owner's direction.

Diagnosis, clarification, comparison, recommendation and revision are advisory *responsibilities*,
each with a prompt and a place in the interface. Which one happens next is a judgement about the
manager's situation, and under BlueCallom's hierarchy that judgement belongs in a prompt.

Each turn works like this:

1. Code assembles the current session state and calls the **next-action prompt**.
2. The prompt returns a chosen action, drawn from a fixed set, with its reasoning.
3. Code validates that choice against the action contract. An unrecognised action is rejected.
4. Code runs the prompt for that action, validates its output against a schema, and commits the
   result to session state through a legal transition.
5. The loop continues or stops. Code enforces the stop conditions.

### The action contract

Every permitted action, the prompt that performs it, and the contract its output must satisfy.
This table is the single source of truth. An earlier revision listed a `diagnose.md` prompt that
had no corresponding action, which meant the prompt could never have been reached. `diagnose` is
now a permitted action in its own right. See decision D-017.

| Action | Chosen when | Prompt | Output contract |
|---|---|---|---|
| `diagnose` | The brief needs reading before anything else: gaps, contradictions and unstated assumptions | `actions/diagnose.md` | `Diagnosis` |
| `request_context` | Essential inputs are absent entirely | `actions/request-context.md` | `ContextRequest` |
| `ask_clarification` | Up to three decision-critical questions would change the advice | `actions/clarify.md` | `ClarificationBatch` |
| `compare` | Enough is known to set out the alternatives honestly | `actions/compare.md` | `Comparison` |
| `recommend` | A comparison exists and a justified choice can be defended | `actions/recommend.md` | `Recommendation` |
| `revise` | A constraint changed after advice was given | `actions/revise.md` | `Revision` |
| `await_user` | Nothing useful can be done until the manager responds | none | `AwaitUser` |

The mapping is declared once in code, as `ACTION_OUTPUT_CONTRACTS` in
`backend/app/models/actions.py`, so the action set and the output contracts cannot drift apart.
`await_user` is the one action with no prompt: it ends the turn and hands control back, so there
is no model output to validate.

A well-specified brief may reach `compare` immediately. A vague one may clarify twice. The order
is an outcome, not a schedule.

### Why the guards are not a violation of the method

[requirements.md](requirements.md) B7 records a verified fact: the BlueCallom source page says
nothing about validation, schemas, limits or control. So these are our engineering judgement, and
we present them as such rather than attributing them to the method.

They are compatible with the hierarchy because they decide nothing. No guard has an opinion about
which initiative is better. They enforce that the loop terminates, that state stays consistent,
that output matches its contract, and that only declared actions run. That is the "precision" case
BlueCallom explicitly reserves for code when the page states that IoC "has nothing to do with
'No-Code'."

The inverse error is the real risk. Moving schema enforcement or iteration caps into prose, to
make the Python smaller, would produce an application that cannot be trusted to stop.

---

## 3. Comparison model

**No weighted numerical scoring in the MVP.** Removed at the project owner's direction.

Each initiative in a comparison carries five separately labelled categories: stated facts,
assumptions, missing evidence, feasibility constraints, and trade-offs. Definitions are in
[requirements.md](requirements.md), C5.

Two consequences for the code:

- The contract gives each category its own field, so a producer has to choose one when writing a
  claim, and a reader can see which was chosen. **This is structural, not epistemic.** It does not
  establish that a statement placed under stated facts is true, nor that something filed as a fact
  was not actually an assumption. A schema cannot tell the difference. What it gives is a
  consistent place to look and something a reviewer or a later check can act on.
- **There is no numeric default anywhere.** A missing value stays missing. The contract has no
  "unknown becomes zero" path, because a zero would be indistinguishable from a measured low, and
  any later ranking would silently punish the option we know least about.

Claims that rest on the manager's input carry lightweight source references naming the brief field
or clarification answer they came from. Referential checks confirm that a referenced identifier
exists. **They do not confirm that the cited input supports the claim.** Traceability makes a
wrong claim findable; it does not make a claim right. See decision D-016.

If scoring is introduced later it arrives with documented scales, documented weights and a written
statement of limitations. It will not appear implicitly.

---

## 4. Directory layout

Implemented parts are marked. Everything else is planned.

```
.
├── README.md                          ✅
├── .env.example                       ✅  placeholders only
├── .gitignore                         ✅
├── package.json                       ✅  root: npm run dev
├── scripts/dev-backend.mjs            ✅  finds the venv interpreter per platform
├── docs/                              ✅
│   ├── requirements.md · architecture.md · decisions.md · worklog.md
│   ├── ui-ux.md                       ⬜  written alongside the interface
│   └── prompts/                       ✅  DEVELOPMENT prompt record, not runtime
├── backend/
│   ├── app/
│   │   ├── main.py                    ✅  FastAPI app, CORS, router mount
│   │   ├── config.py                  ✅  env loading, no secrets in code
│   │   ├── api/routes.py              ✅  health only so far
│   │   ├── core/
│   │   │   ├── advisory.py            ✅  bounded loop; runs what the prompt chose
│   │   │   ├── assemble.py            ✅  builds inputs; fences manager text
│   │   │   ├── prompt_loader.py       ✅  reads prompts/ per call, hashes contents
│   │   │   ├── model_client.py        ✅  OpenAI adapter, named failures
│   │   │   ├── limits.py              ✅  action, request, size and time ceilings
│   │   │   └── validation.py          ✅  the single boundary before state
│   │   ├── models/                    ✅  declared contracts, tested
│   │   │   ├── common.py              ✅  identifiers, source references, strict base
│   │   │   ├── brief.py               ✅  objectives, constraints, initiatives
│   │   │   ├── clarification.py       ✅  questions, answered / skipped / unanswered
│   │   │   ├── comparison.py          ✅  the five categories
│   │   │   ├── recommendation.py      ✅  advice and revision
│   │   │   ├── actions.py             ✅  permitted actions, action-to-output map
│   │   │   └── references.py          ✅  referential integrity only
│   │   ├── data/                      ✅  one fictional worked example, hand-authored
│   │   ├── store/session.py           ⬜  append-only session history
│   │   ├── export/render.py           ⬜  Markdown / JSON brief
│   │   └── data/scenarios/            ⬜  fictional sample scenarios
│   ├── prompts/                       ✅  RUNTIME prompts: the product's intelligence
│   ├── fixtures/                      ⬜  recorded responses, labelled as sample data
│   ├── tests/                         ⬜
│   └── requirements.txt               ✅
└── frontend/
    ├── index.html · package.json · vite.config.ts · tsconfig.json   ✅
    └── src/
        ├── main.tsx · App.tsx         ✅
        ├── api/client.ts              ✅  health check only
        ├── components/                ✅  layout shell, non-functional
        └── styles/                    ✅  design tokens
```

`docs/prompts/` and `backend/prompts/` are kept apart deliberately. The first records how the
software was built. The second is the software.

---

## 5. Responsibilities

### 5.1 Runtime prompts — `backend/prompts/` (not yet written)

| Prompt | Owns |
|---|---|
| `system/advisor.md` | Persona, tone, refusal behaviour, the standing rule that an unknown is never presented as a finding |
| `actions/next-action.md` | Choosing the next advisory action from the permitted set, with reasoning |
| `actions/diagnose.md` | Naming gaps, contradictions and unstated assumptions in the brief |
| `actions/request-context.md` | Stating which essential inputs are missing before anything else can proceed |
| `actions/clarify.md` | Choosing at most three questions that would actually change the advice |
| `actions/compare.md` | Deriving relevant criteria; producing the five-category comparison |
| `actions/recommend.md` | A justified choice, traceable to facts and labelled assumptions, with risks and first moves |
| `actions/revise.md` | Re-evaluating after a change and explaining what moved, what held, and why |
| `support/repair-output.md` | Restating a malformed response so it satisfies its schema |

Each carries front matter declaring identifier, version, role, inputs, outputs and constraints.
Prompts are loaded from disk at runtime, never embedded in Python string literals, so the
method's claim that better models give better results without code changes can actually be
exercised.

### 5.2 Code — `backend/app/`

**Model communication.** One interface with concrete adapters. Handles authentication, timeouts,
retries, and the fixture mode. It contains no business rules. A live call that fails raises; it
never falls back to a fixture.

**Guards.** Execution limits, the permitted action contract, and legal state transitions. Pure,
testable, no model access.

**Validation.** Model output is parsed into declared contracts. One repair pass, then surfaced as
an error.

**State management.** Session state is append-only, so a revision can be diffed against what
preceded it. That diff is what lets the interface show what changed.

**Exports.** A completed session rendered as a Markdown decision brief and a JSON payload,
including open unknowns and labelled assumptions.

### 5.3 Frontend — `frontend/src/`

Presentation and interaction only. It never decides a recommendation and never calls a model
provider directly. No API key ever reaches the browser.

---

## 6. Technology choices

### React with Vite and TypeScript

**Suitability.** The interface is several coordinated panels over one evolving session object,
with partial updates arriving per advisory turn. That is React's core competence.

**Maintainability.** TypeScript makes the API contract explicit at the boundary where this
application is most likely to break silently, which is the shape of the data coming back from the
backend. Since every response is already a declared Pydantic contract, mirroring it in TypeScript
costs little and catches drift at compile time rather than in a demonstration.

To correct an overstatement in the previous revision of this document: **TypeScript does not
conflict with Intelligence-over-Code, and neither does a component library.** The method's
hierarchy concerns where *business judgement* lives, not which typing discipline or UI toolkit the
presentation layer uses. Types and components carry no opinion about which initiative a manager
should fund.

**On component libraries.** We are starting with plain CSS modules and a small design-token file,
because assessment part 3 asks us to explain the UI/UX decisions and a hand-built layout makes
those decisions ours to explain. This is a presentation choice about the deliverable, not a
methodological objection. If the interface work later needs accessible primitives such as dialogs,
comboboxes or focus management, adopting a headless library would be an improvement rather than a
compromise.

**Vite** for a dev server that needs no build configuration, and for the proxy that removes CORS
handling from the developer's concerns.

### Python with FastAPI

**Suitability.** Pydantic. Validating model output against a declared contract is the single most
important piece of code in an application of this kind, and FastAPI makes that the default path
rather than an add-on. The Python SDK ecosystem for model providers is the most mature.

**Maintainability.** Generated OpenAPI documentation keeps the HTTP surface described without a
separate document that drifts. Guards and validation are pure Python functions, fully unit
testable without a model.

### Alternative considered

A single Next.js application with API routes would remove a process and a port, and would be a
perfectly reasonable way to build this.

We chose the two-process split on suitability and familiarity, not on principle. Pydantic gives
the strongest declarative contract-and-validation story of the options available, which matters
because parsing model output is the code this application leans on most. The project owner is more
productive in Python for that layer. A separate backend also keeps the runtime prompt files beside
the code that loads them, which suits how we intend to review them.

**We make no claim that Next.js or TypeScript would compromise Intelligence-over-Code.** An
earlier revision said it would blur the boundary between interface and intelligence. That was
wrong, and it is withdrawn. Where business judgement lives is a matter of how an application is
organised, not of which language or framework holds the transport layer. The same separation is
achievable in a single TypeScript project. See decision D-018.

### Model provider

**Deliberately open**, pending confirmation of available API access. The model client is defined
as an interface with adapters behind it, so the choice does not block the skeleton, the guards or
the interface. See [requirements.md](requirements.md), D-b.

---

## 7. Local execution

First-time setup and the single startup command are documented in the [README](../README.md).
After setup, from the repository root:

```
npm run dev
```

This runs `concurrently`, starting Uvicorn with reload and the Vite dev server. It behaves
identically on Windows, macOS and Linux, which a Makefile would not. Frontend requests to `/api`
are proxied to the backend by Vite, so no CORS configuration is needed in development.

Credentials live in a git-ignored `.env`. `.env.example` is committed and contains placeholders
only.

---

## 8. Dependencies

**Backend.** `fastapi`, `uvicorn[standard]`, `pydantic`, `pydantic-settings`, `python-dotenv`,
`pyyaml` for prompt front matter. Later: a provider SDK, plus `pytest` and `httpx` for tests.

**Frontend.** `react`, `react-dom`, `vite`, `typescript`, `@vitejs/plugin-react`.

**Root.** `concurrently`, dev dependency only.

Deliberately short. Every dependency in an assessment repository is something a reviewer must
install before they can judge the work.

---

## 9. Known risks

1. **Prompt output drift.** Free-form output will not always satisfy a schema. Mitigated by the
   repair pass and by requesting structured output through the provider's native mechanism.
2. **Loop cost and latency.** An adaptive loop can take more turns than a fixed pipeline. This is
   why the execution limits exist. Real figures will be measured once model calls are implemented,
   not guessed at here.
3. **Unknowns leaking into confidence.** The failure mode we most want to avoid is advice that
   reads as certain because an assumption lost its label in transit. Mitigated by the separate
   schema fields of section 3, and testable.
4. **Method theatre.** The characteristic failure of an IoC project is a codebase claiming prompt
   primacy while business rules accumulate in Python conditionals. Acceptance criterion C9.1 is
   the check: if editing only a prompt file cannot change the advice, the design has failed.
