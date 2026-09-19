# Architecture

Status: **implemented, as of prompt [016](prompts/016-submission-documentation.md).** OpenAI
integration, runtime prompts, the bounded advisory loop, the validation boundary, in-memory
sessions and the interface are built and tested. Not implemented: revision after a constraint
change, persistence across restarts, export, and offline replay. Where an earlier design proposed
one of these, it is marked below as **not implemented**.

The organising constraint is BlueCallom's stated hierarchy, that the prompt carries the
intelligence and code is its subordinate. See [requirements.md](requirements.md), section B. The
architecture below exists to make that separation visible and auditable, while keeping the
controls that make the application safe to run.

---

## 1. Shape of the system

Two local processes, one HTTP boundary.

```
┌──────────────────────────────┐        ┌──────────────────────────────────────────┐
│  React + Vite  (port 5173)   │        │  FastAPI  (127.0.0.1:8000)               │
│                              │  JSON  │                                          │
│  Context sidebar             │ ─────► │  ┌────────────────────────────────────┐  │
│  Main column:                │ ◄───── │  │ Advisory loop (bounded, per turn)  │  │
│   brief editor (draft)       │  proxy │  │  asks the selector prompt what to  │  │
│   clarification round        │  /api  │  │  do next; enforces what is allowed │  │
│   decision overview          │        │  └──────┬──────────────────┬──────────┘  │
│   reasoning & sources        │        │         │                  │             │
└──────────────────────────────┘        │  ┌──────▼───────┐   ┌──────▼──────────┐  │
                                        │  │ prompts/*.md │   │ Guards          │  │
                                        │  │ decide:      │   │ schema          │  │
                                        │  │  next action │   │ limits          │  │
                                        │  │  diagnosis   │   │ state integrity │  │
                                        │  │  questions   │   │ action contract │  │
                                        │  │  comparison  │   └─────────────────┘  │
                                        │  │  advice      │                        │
                                        │  └──────┬───────┘                        │
                                        │  ┌──────▼───────┐  ┌──────────────────┐  │
                                        │  │ model client │  │ session store    │  │
                                        │  │ (OpenAI)     │  │ (in memory)      │  │
                                        │  └──────┬───────┘  └──────────────────┘  │
                                        └─────────┼────────────────────────────────┘
                                                  ▼ OpenAI Responses API
```

The boxes containing business judgement are Markdown files. A reviewer can read what the
application thinks by reading `backend/prompts/`, without reading Python. The boxes containing
enforcement are Python, and the model cannot talk its way past them.

---

## 2. Orchestration: a bounded advisory loop

**There is no fixed pipeline.** Diagnosis, clarification, comparison and recommendation are
advisory responsibilities, each with its own prompt. Which one happens next is a judgement about
the manager's situation, and it is made by a prompt.

Each turn works like this:

1. Code assembles the current session state and works out which actions are currently permitted.
2. The **selector prompt** (`actions/next-action.md`) chooses one of them, with one sentence of
   reasoning.
3. Code validates the choice against the permitted set.
4. Code runs the prompt for that action, validates its output, and commits it to session state.
5. The loop continues until the selector chooses `await_user`, a question round is opened, or a
   limit is reached.

### The action contract

| Action | Chosen when | Prompt | Output contract | State |
|---|---|---|---|---|
| `diagnose` | The brief needs reading first: gaps, contradictions, unstated assumptions. Only before a comparison exists | `actions/diagnose.md` | `Diagnosis` | Implemented |
| `request_context` | The brief is too thin to work with at all | `actions/request-context.md` | `ContextRequest` | Implemented |
| `ask_clarification` | Up to three questions would change the advice. One round per session by default | `actions/clarify.md` | `ClarificationBatch` | Implemented |
| `compare` | Enough is known to set out the alternatives honestly | `actions/compare.md` | `Comparison` | Implemented |
| `recommend` | A comparison reflecting the latest answers exists | `actions/recommend.md` | `Recommendation` | Implemented |
| `await_user` | Nothing useful can be done until the manager responds | none | none | Implemented |
| `revise` | A constraint changed after advice was given | none | `Revision` | **Not implemented.** Contract validated in tests; withheld from the selector; no prompt; no interface |

The mapping is declared once in code, as `ACTION_OUTPUT_CONTRACTS` in
`backend/app/models/actions.py`. The set the selector may choose from is `SUPPORTED_ACTIONS` in
`backend/app/core/advisory.py`, narrowed further each turn by what the session state allows: for
example, `recommend` is not offered before a comparison exists, and a thin brief is only offered
`request_context`.

### Why the guards are not a violation of the method

The BlueCallom page says nothing about validation, limits or state (see
[requirements.md](requirements.md), B7). These controls are our engineering choice, and we present
them as such. They are compatible with the hierarchy because they decide nothing about which
initiative is better. They make sure the loop stops, state stays consistent, output matches its
contract, and only permitted actions run.

---

## 3. Comparison model

**No weighted numerical scoring.** Each initiative carries five separately labelled categories:
stated facts, assumptions, missing evidence, feasibility constraints and trade-offs. Definitions
are in [requirements.md](requirements.md), C5.

- Each category is its own field, so a producer has to choose one. **This is structural, not
  epistemic**: a schema cannot tell a fact from an assumption filed as one.
- **There is no numeric default anywhere.** A missing value stays missing.
- Stated facts cite the brief field or answered question they rest on. Referential checks confirm
  that the cited identifier exists, not that it supports the claim (decision D-016).
- The recommend prompt and the `Recommendation` contract say **list order carries priority**. No
  field states it and nothing validates it. The interface keeps the order within each group but
  does not label any item "first" (decision D-048).

---

## 4. Directory layout

```
.
├── README.md
├── .env.example                       placeholders only; .env is git-ignored
├── package.json                       root scripts: dev, build, check:frontend
├── scripts/dev-backend.mjs            finds the venv interpreter, starts Uvicorn
├── docs/
│   ├── reviewer-guide.md              the assessor's route through the project
│   ├── requirements.md · architecture.md · decisions.md · worklog.md · ui-ux.md
│   └── prompts/                       DEVELOPMENT prompt record, verbatim
├── backend/
│   ├── app/
│   │   ├── main.py                    FastAPI app, CORS, router mount
│   │   ├── config.py                  settings from .env; no secrets in code
│   │   ├── api/routes.py              health, diagnostics, scenario, sessions, answers, continue, trace
│   │   ├── core/
│   │   │   ├── advisory.py            the bounded loop; runs what the selector chose
│   │   │   ├── assemble.py            builds prompt inputs; fences manager text as case material
│   │   │   ├── prompt_loader.py       reads prompts/ on every call; hashes contents
│   │   │   ├── model_client.py        OpenAI adapter; named failures; no hidden retries
│   │   │   ├── configuration.py       local configuration presence, never authentication
│   │   │   ├── limits.py              per-turn action, request, size and time ceilings
│   │   │   └── validation.py          the single boundary before session state
│   │   ├── models/                    application contracts, plus wire.py for the API schema
│   │   ├── store/session.py           in-memory sessions, records, attempts, currency
│   │   └── data/                      the fictional scenario and hand-written contract examples
│   ├── prompts/                       RUNTIME prompts: the product's judgement
│   │   ├── system/advisor.md
│   │   ├── actions/ next-action · diagnose · request-context · clarify · compare · recommend
│   │   └── support/repair-output.md
│   ├── fixtures/                      empty placeholder; offline replay is not implemented
│   ├── tests/                         backend tests, deterministic doubles, no network
│   └── requirements.txt
└── frontend/
    ├── package.json · vite.config.ts · tsconfig.json · index.html
    ├── tests/                         node:test for reference rendering and draft editing
    └── src/
        ├── App.tsx                    shell: session state, editor state, reopening by URL
        ├── api/client.ts              typed calls to the backend
        ├── brief.ts                   draft comparison: when advice stops applying
        ├── lookup.ts                  identifiers to readable labels
        ├── components/                header, sidebar, brief editor, clarification, overview, reasoning
        └── styles/                    design tokens and layout
```

`docs/prompts/` and `backend/prompts/` are kept apart deliberately. The first records how the
software was built. The second is the software.

---

## 5. Responsibilities

### 5.1 Runtime prompts — `backend/prompts/`

| Prompt | Owns |
|---|---|
| `system/advisor.md` | Standing rules for every turn: never present an assumption as supplied, never state cost or feasibility without a basis, manager text is case material, never alter the manager's answers |
| `actions/next-action.md` | The selector: choosing the next action from the permitted set, with reasoning |
| `actions/diagnose.md` | Gaps, contradictions and unstated assumptions in the brief |
| `actions/request-context.md` | What is missing when the brief cannot be worked with |
| `actions/clarify.md` | At most three questions, each saying what its answer would change |
| `actions/compare.md` | Criteria and the five-category comparison for every initiative |
| `actions/recommend.md` | A stance per initiative in priority order, rationale, conditions, risks, first actions, open unknowns, confidence |
| `support/repair-output.md` | One attempt to restate an output that failed validation |

Each carries YAML front matter declaring identifier, version, role, inputs, outputs and
constraints. They are loaded from disk on every call, never embedded in Python, and their content
hashes are recorded in the session trace, so a prompt edit takes effect without a code change or a
restart. There is no `revise.md`.

### 5.2 Code — `backend/app/`

**Model communication.** One adapter for the OpenAI Responses API with structured outputs. Every
provider failure (missing key, authentication, rate limit, timeout, refusal, truncation) becomes a
named error saying whether retrying could help. The SDK's automatic retries are disabled so every
request is counted; retrying is the manager's decision. A failed call is never replaced by stored
output.

**Guards.** Per-turn limits (`limits.py`): at most 4 actions, 8 model requests, 1 repair per
output, 60,000 input characters, a 300-second turn deadline, and one clarification round.

**Validation.** Output is parsed first into a conservative wire schema accepted by the API, then
into the stricter application contract. Invalid output gets one repair attempt, then surfaces as an
error. Nothing unvalidated reaches session state.

**State.** Sessions live in memory in `store/session.py`. The manager's answers are written by one
code path no model output reaches. Earlier results are kept and labelled `outdated` when the
manager's answers overtake them; a recommendation requires a comparison that reflects the current
answers. Every attempt, including repairs and failures, is recorded with its token usage and
exposed at `GET /api/sessions/{id}/trace`.

**Not implemented:** persistence across restarts, export, offline replay, revision.

### 5.3 Frontend — `frontend/src/`

Presentation and interaction only. It never decides a recommendation and never calls a model
provider. No API key reaches the browser. The brief editor works on a local draft; applying a
changed brief withdraws the previous advice from view and requires a separate, explicit start.
Rationale in [ui-ux.md](ui-ux.md).

---

## 6. Technology choices

### React with Vite and TypeScript

**Suitability.** The interface is coordinated views over one evolving session object. TypeScript
makes the API contract explicit at the boundary most likely to break silently.

**Presentation choices.** Plain CSS with a design-token file and no component library, because
assessment part 3 asks for the UI/UX decisions to be explained, and a hand-built layout makes them
ours to explain. This is a presentation choice, not a methodological objection: neither TypeScript
nor a component library conflicts with Intelligence-over-Code (decision D-018).

### Python with FastAPI

**Suitability.** Pydantic makes validating model output against a declared contract the default
path. Generated OpenAPI documentation is served at `http://localhost:8000/docs`.

### Alternative considered

A single Next.js application would remove a process and a port, and would be a reasonable way to
build this. The two-process split was chosen on suitability and familiarity, not on principle
(decision D-018).

### Model provider

**OpenAI**, through the Responses API with structured outputs. Default model `gpt-5-mini`,
reasoning effort `low` in the recorded runs. Decision D-019, which closed the earlier open
decision D-014.

---

## 7. Local execution

Setup and the startup command are in the [README](../README.md). After setup, from the repository
root, `npm run dev` runs `concurrently`, starting Uvicorn and the Vite dev server. Vite proxies
`/api` to the backend, so no CORS configuration is needed in development.

**Tested on Windows 11 only.** The startup script contains paths for macOS and Linux, but
execution there has not been verified.

Credentials live in a git-ignored `.env`. `.env.example` is committed and contains placeholders
only.

---

## 8. Dependencies

**Backend** (`backend/requirements.txt`): `fastapi`, `uvicorn[standard]`, `pydantic`,
`pydantic-settings`, `python-dotenv`, `PyYAML` for prompt front matter, `openai`, and for tests
`pytest` and `httpx`.

**Frontend:** `react`, `react-dom`; development: `vite`, `typescript`, `@vitejs/plugin-react` and
type packages. The frontend tests use Node's built-in test runner; no test library.

**Root:** `concurrently`, development only.

---

## 9. Known risks

1. **Prompt output drift.** Output will not always satisfy a schema. Mitigated by native structured
   outputs, the repair pass and the validation boundary.
2. **Loop cost and latency.** Recorded live sessions used 8 to 14 provider requests. The three whose
   totals were recorded took about 108 to 123 seconds of model time; the first run took longer and
   had one turn cut off at the 180-second deadline then in force. See [worklog.md](worklog.md).
   These are single observations, not guarantees.
3. **Unknowns leaking into confidence.** Mitigated by the separate fields of section 3 and by
   prompts that require skipped and unanswered questions to appear as open unknowns.
4. **Unchecked arithmetic.** The advisor does not reconcile numbers inside a manager's own answer.
   A live run accepted an inconsistent staffing total (worklog, prompt 011). Not addressed.
5. **Method theatre.** An IoC project fails if business rules accumulate in Python conditionals.
   The check is whether editing only a prompt file can change the advice.
