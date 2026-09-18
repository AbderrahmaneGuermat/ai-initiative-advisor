# Proposed architecture

Status: **proposed, awaiting review.** No code exists yet.

The organising constraint is BlueCallom's rule that the prompt carries the intelligence and code
carries the mechanics (see [requirements.md](requirements.md), B2 and B3). The architecture below
exists mainly to make that separation visible and auditable, rather than merely claimed.

---

## 1. Shape of the system

Three parts, one process boundary.

```
┌─────────────────────────────┐        ┌──────────────────────────────────────┐
│  React + Vite  (port 5173)  │  HTTP  │  FastAPI  (port 8000)                │
│                             │ ─────► │                                      │
│  Context panel              │  JSON  │  ┌────────────────────────────────┐  │
│  Advisory thread            │ ◄───── │  │ Orchestrator (thin)            │  │
│  Ranking panel              │        │  │  loads prompt, calls model,    │  │
│                             │        │  │  validates, stores, returns    │  │
└─────────────────────────────┘        │  └───────────┬────────────────────┘  │
                                       │              │                       │
                                       │   ┌──────────▼──────────┐            │
                                       │   │ prompts/  (*.md)    │  ◄── the   │
                                       │   │ diagnose, clarify,  │      real  │
                                       │   │ compare, recommend, │      logic │
                                       │   │ revise, repair      │            │
                                       │   └──────────┬──────────┘            │
                                       │              │                       │
                                       │   ┌──────────▼──────────┐            │
                                       │   │ model adapter       │ ──► LLM API│
                                       │   └─────────────────────┘            │
                                       │   ┌─────────────────────┐            │
                                       │   │ scoring · schemas · │            │
                                       │   │ session store · exp │            │
                                       │   └─────────────────────┘            │
                                       └──────────────────────────────────────┘
```

The important property: the boxes on the right that contain business judgement are Markdown
files, not Python modules. A reviewer can read what the application thinks by reading
`backend/prompts/`, without reading any code.

---

## 2. Proposed directory layout

```
.
├── README.md
├── .env.example
├── package.json                 # root: one dev command
├── docs/
│   ├── requirements.md
│   ├── architecture.md
│   ├── decisions.md
│   ├── worklog.md
│   ├── ui-ux.md                 # written alongside the interface
│   └── prompts/                 # DEVELOPMENT prompt record (not runtime)
│       └── 001-project-brief.md
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, router mount
│   │   ├── api/routes.py        # HTTP surface
│   │   ├── core/
│   │   │   ├── orchestrator.py  # stage sequencing; deliberately thin
│   │   │   ├── prompt_loader.py # reads prompts/, parses front matter
│   │   │   ├── model_client.py  # provider adapter + retries
│   │   │   ├── validation.py    # Pydantic parse + repair loop
│   │   │   └── scoring.py       # weighted arithmetic only
│   │   ├── models/schemas.py    # Pydantic contracts
│   │   ├── store/session.py     # session state, JSON persistence
│   │   ├── export/render.py     # Markdown / JSON brief
│   │   └── data/scenarios/      # fictional demo scenarios
│   ├── prompts/                 # RUNTIME prompts — the product's intelligence
│   │   ├── system/advisor.md
│   │   ├── stages/01-diagnose.md
│   │   ├── stages/02-clarify.md
│   │   ├── stages/03-compare.md
│   │   ├── stages/04-recommend.md
│   │   ├── stages/05-revise.md
│   │   └── support/repair-output.md
│   ├── tests/
│   ├── fixtures/                # recorded model responses for offline mode
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── package.json
    └── src/
        ├── App.tsx
        ├── api/client.ts
        ├── state/session.ts
        ├── components/          # ContextPanel, AdvisoryThread, RankingPanel, ...
        └── styles/
```

`docs/prompts/` and `backend/prompts/` are kept apart on purpose, as the brief requires. The
first is the record of how the software was built. The second is the software.

---

## 3. Responsibilities, stated precisely

### 3.1 Runtime prompts — `backend/prompts/`

These own every judgement the product makes.

| File | Owns |
|---|---|
| `system/advisor.md` | Persona, tone, refusal behaviour, the standing rule that unsupported claims are not made |
| `stages/01-diagnose.md` | Reading the brief; naming gaps, contradictions and unstated assumptions |
| `stages/02-clarify.md` | Choosing which three to six questions actually change the answer |
| `stages/03-compare.md` | Deriving the criteria for this manager; scoring each initiative with reasoning |
| `stages/04-recommend.md` | Ranking, justification, risks, sequencing |
| `stages/05-revise.md` | Re-evaluating after a constraint change and explaining the delta |
| `support/repair-output.md` | Restating a malformed response so it satisfies the schema |

Each file carries front matter declaring identifier, version, role, inputs, outputs and
constraints, per requirement C3.

### 3.2 Code — `backend/app/`

Code does five things and no more.

**Model communication.** `model_client.py` holds one interface with a `complete(prompt, context)`
method, plus concrete adapters. It handles authentication, timeouts, retries with backoff, token
accounting and the offline fixture mode. It contains no business rules.

**State management.** `store/session.py` holds the session: scenario, objectives, constraints,
candidate initiatives, clarification answers, stage outputs, and a revision history. Persisted as
one JSON file per session, so a revision diff is inspectable.

**Validation.** `validation.py` parses model output into Pydantic models. On failure it runs one
repair pass through `support/repair-output.md`, then surfaces the error rather than rendering
something unverified. This satisfies acceptance criterion C7.5.

**Calculation.** `scoring.py` takes criterion weights and per-initiative scores that the model
produced, and computes weighted totals, ranks and the delta between two revisions. Pure
functions, fully unit tested, no model access. This is the clearest example of BlueCallom's B3
boundary: the model judges, Python counts.

**Exports.** `export/render.py` turns a completed session into a Markdown decision brief and a
JSON payload.

### 3.3 Frontend — `frontend/src/`

Presentation and interaction only. It never computes a ranking and never calls a model directly.
It holds the API key nowhere; all model traffic goes through the backend.

---

## 4. Request flow, one advisory session

1. Manager picks a fictional scenario, or enters their own objectives, constraints and
   candidate initiatives. `POST /api/sessions`.
2. `POST /api/sessions/{id}/diagnose` — orchestrator loads `01-diagnose.md`, injects the session
   state, calls the model, validates, stores. Returns gaps and assumptions.
3. `POST /api/sessions/{id}/clarify` returns the questions. **HIP 1:** the UI waits. The manager
   answers or skips. `POST /api/sessions/{id}/answers` records the replies.
4. `POST /api/sessions/{id}/compare` — the model derives criteria and scores each initiative with
   per-criterion reasoning. Python computes weighted totals from those scores.
5. `POST /api/sessions/{id}/recommend` — ranked shortlist, justification, risks, first moves.
6. **HIP 2:** the manager edits a constraint. `POST /api/sessions/{id}/revise` re-runs comparison
   and recommendation under the new constraint, and the response includes an explicit delta:
   what moved, what held, and why.
7. `GET /api/sessions/{id}/export?format=md|json`.

The orchestrator is deliberately dull. Its job is to load the right prompt file, assemble
context, call the adapter, validate and store. Any temptation to put a business rule there is a
signal that the rule belongs in a prompt.

---

## 5. Technology choices

### Frontend: React with Vite and TypeScript — accepted as proposed

React is the right call here and I am not proposing an alternative. Three panels with shared
session state is exactly its comfort zone, it is the most reviewable choice for an assessor, and
Vite gives a fast dev server with no build configuration. TypeScript is a small addition that
pays for itself because the API contract is the thing most likely to drift.

State via React Context plus `useReducer`. The session is one object with a small number of
transitions. Redux or Zustand would be ceremony at this size.

Styling via plain CSS modules with a small design-token file. A component library would make the
UI/UX rationale in requirement A4 harder to defend, since the decisions would be the library's
rather than ours.

### Backend: Python with FastAPI — accepted as proposed

Also the right call. Pydantic is the decisive factor: validating model output against a declared
schema is the single most important piece of code in an IoC application, and FastAPI gives that
plus generated OpenAPI documentation for free. The Python AI SDK ecosystem is the most mature.

### One alternative I want to flag, and reject

A single Next.js application with API routes would remove a process and a port. I recommend
against it for this project. It would put the prompt-handling logic in TypeScript, where schema
validation is weaker than Pydantic, and it would blur the boundary between interface and
intelligence that the whole assessment is about. The two-process split is slightly more setup for
a much clearer demonstration of the method.

### Model provider

A thin adapter with Claude as the default. See decision D1 in [requirements.md](requirements.md).
The adapter is roughly fifty lines and means a missing or rate-limited key does not end the demo.

---

## 6. Local execution

First-time setup, three commands:

```
npm install                                   # root + frontend deps
python -m venv backend/.venv                  # then activate
pip install -r backend/requirements.txt
```

Thereafter, one command from the repository root:

```
npm run dev
```

This uses `concurrently` to start Uvicorn with reload on port 8000 and Vite on port 5173. It
works identically on Windows, macOS and Linux, which a Makefile would not. Frontend calls are
proxied to the backend through Vite, so there is no CORS configuration for the developer to get
wrong.

Credentials live in `.env` at the repository root, which is git-ignored. `.env.example` will list
every variable with a comment, and will be committed. Expected variables: the model provider
name, the provider API key, the model identifier, and an offline-mode flag.

Without a key, the application runs in offline mode against recorded fixtures, so it can be
reviewed by someone who has no credentials.

---

## 7. Dependencies

**Backend:** `fastapi`, `uvicorn[standard]`, `pydantic`, `python-dotenv`, `pyyaml` for prompt
front matter, the chosen provider SDK, and `pytest` plus `httpx` for tests.

**Frontend:** `react`, `react-dom`, `vite`, `typescript`. Nothing else planned.

**Root:** `concurrently`, as a dev dependency only.

The list is short on purpose. Every dependency in an assessment repository is something the
assessor has to install before they can judge the work.

---

## 8. Known risks in this design

1. **Prompt output drift.** Free-form model output will not always satisfy a schema. Mitigated by
   the repair pass, and by asking for structured output through the provider's native mechanism
   rather than by pleading in prose.
2. **Latency.** Five sequential model calls is slow. Compare and recommend may need to merge, or
   the UI must show honest per-stage progress. To be measured once real calls exist, not guessed.
3. **Cost of the demo.** A full session is five calls over a moderate context. Offline mode is
   the answer for repeated review.
4. **Method theatre.** The genuine risk in an IoC project is a codebase that claims prompt
   primacy while hiding business rules in Python conditionals. Acceptance criterion C7.1 is the
   check: if editing only a prompt file cannot change the advice, the design has failed.
