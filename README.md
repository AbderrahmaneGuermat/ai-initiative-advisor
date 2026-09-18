# AI Initiative Advisor

A strategy-consulting application for managers, built according to BlueCallom's
Intelligence-over-Code method. It helps a manager prioritise a portfolio of candidate enterprise
AI initiatives against their objectives, resources and constraints.

The application diagnoses the brief, asks the clarification questions that would actually change
the answer, compares the alternatives with their evidence and assumptions labelled, gives a
justified recommendation, and revises that recommendation when a constraint changes.

---

## Assessment scope

This repository addresses **parts 2 and 3** of the assessment:

- **Part 2.** Build a strategy-consulting application for managers using the IoC method.
- **Part 3.** Design a sample enterprise AI interface and explain the UI/UX decisions.

**Part 1, the candidate's existing professional projects, is presented separately and is not this
repository.** This application was built specifically for the assessment, beginning on
2026-09-18. It is not evidence of earlier professional work, and nothing here should be read as
implying otherwise. The Git history shows exactly when it was written.

---

## Current status

**Data contracts stage.** The project runs, and the contracts that the advisory exchange will use
are written and tested. **No advisory behaviour exists.** No AI model is connected, no prompt is
executed, and nothing in the application can produce a comparison or a recommendation. The
interface is a layout shell that labels itself an unfinished prototype.

The distinction that matters throughout this repository is between a capability that **works** and
one that is **specified**. Specified means written down in the documentation and, where relevant,
given a data contract. It does not mean it does anything.

| Capability | State |
|---|---|
| Repository, documentation, development prompt record | **Works** |
| One-command startup, `npm run dev` | **Works**, verified |
| Backend health endpoint, reporting its own build stage | **Works**, verified |
| Frontend shell and layout regions | **Works**, placeholders only |
| Frontend to backend connection | **Works**, verified through the dev proxy |
| Data contracts for brief, clarification, comparison, recommendation, revision, next action | **Works**, 44 tests |
| Reference resolution against the brief and answered questions | **Works**, tested |
| One fictional worked example, validated against the contracts | **Works**, hand-authored, not model output |
| Model calls, runtime prompts, advisory loop | **Specified only** |
| Producing a comparison, recommendation or revision | **Specified only** |
| Sessions, persistence, export, offline fixture replay | **Specified only** |
| Interface beyond the layout shell | **Specified only** |

Nothing in the application generates advice. The example payloads under `backend/app/data/` were
written by hand to exercise the contracts, and are labelled as such wherever they appear.

Four decisions remain open, including the model provider, which is deliberately deferred until API
access is confirmed. See [docs/requirements.md](docs/requirements.md), section D-b.

---

## Method, in brief

BlueCallom states that **"Prompt is King"** and **"Code is a subordinate of the King,"** and that
IoC **"has nothing to do with 'No-Code'."** Source:
<https://bluecallom.com/intelligence-over-code-method/>

Our reading, and how this project applies it:

- **Prompts decide.** Which advisory action to take next, which questions matter, which criteria
  are relevant, what to recommend, and how to explain a change of advice. These live as Markdown
  files in `backend/prompts/`, not as string literals in Python.
- **Code enforces.** Schema validation, execution limits, state integrity and the contract of
  permitted actions. None of these decides anything about which initiative is better.
- **There is no fixed pipeline.** Diagnosis, clarification, comparison, recommendation and
  revision are advisory responsibilities, not a mandatory sequence. A well-specified brief may go
  straight to comparison.
- **Comparison is qualitative.** No weighted scoring in the first version. Each option is set out
  through stated facts, assumptions, missing evidence, feasibility constraints and trade-offs, so
  a manager can see what the advice rests on. An unknown is never converted into a zero.

The BlueCallom page says nothing about validation, limits or control mechanisms. The controls in
this project are therefore our engineering judgement, and the documentation says so rather than
attributing them to the method.

---

## What is where

| Path | Contents |
|---|---|
| [docs/requirements.md](docs/requirements.md) | Assessment scope, what BlueCallom states, our interpretation, open decisions |
| [docs/architecture.md](docs/architecture.md) | Architecture, the advisory loop, responsibilities, technology rationale |
| [docs/decisions.md](docs/decisions.md) | Decision record, including superseded decisions and why they changed |
| [docs/worklog.md](docs/worklog.md) | What was actually done, what was checked, what is unresolved |
| [docs/prompts/](docs/prompts/) | Chronological record of the development instructions, verbatim |

Two distinct kinds of prompt live in this repository and are deliberately kept apart.
`docs/prompts/` records the instructions used to build the software. `backend/prompts/`, once it
exists, will contain the prompts the software executes at runtime. The first explains how this was
made. The second is the product.

---

## Setup and local execution

Verified on Windows 11 with Node 24.17.0, npm 11.13.0 and Python 3.14.5.

**Prerequisites:** Node.js 20 or later, Python 3.11 or later, Git.

### First-time setup

Run these once, from the repository root.

**Windows (PowerShell):**

```powershell
npm install

python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install --upgrade pip
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

Copy-Item .env.example .env
```

**macOS and Linux:**

```bash
npm install

python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install --upgrade pip
backend/.venv/bin/python -m pip install -r backend/requirements.txt

cp .env.example .env
```

You do not need to activate the virtual environment. The startup script finds the interpreter
inside `backend/.venv` on either platform, and tells you what to run if it is missing.

`npm install` also installs the frontend packages, because `frontend` is an npm workspace of the
root project.

### Starting the application

One command, from the repository root:

```bash
npm run dev
```

This starts the FastAPI backend on port 8000 and the Vite dev server on port 5173, and stops both
if either fails.

Then open **<http://localhost:5173>**.

Prefer `localhost` over `127.0.0.1` for the interface. On the Windows 11 machine this project was
developed and tested on, the dev server bound only the IPv6 loopback, so `http://localhost:5173`
worked while `http://127.0.0.1:5173` refused the connection. That was observed on one machine and
is not claimed as universal behaviour. The address the dev server prints on startup is the one to
trust.

The backend listens on IPv4 at the fixed address `127.0.0.1:8000` and answers on both
`http://127.0.0.1:8000` and `http://localhost:8000`.

**These addresses are not configurable.** They are set in `scripts/dev-backend.mjs` and
`frontend/vite.config.ts`. Change both together if you need different ones.

### Checking it works

```bash
curl http://localhost:8000/api/health
```

The response states the build stage and lists which capabilities exist, so it is obvious how much
of the application is real:

```json
{
  "status": "ok",
  "stage": "data-contracts",
  "implemented": ["health", "data contracts", "contract validation", "reference resolution"],
  "not_implemented": ["model calls", "runtime prompts", "advisory loop", "..."]
}
```

To run the contract tests:

```bash
backend\.venv\Scripts\python.exe -m pytest backend      # Windows
backend/.venv/bin/python -m pytest backend                # macOS, Linux
```

The interface shows the same thing as a status indicator in its header. Interactive API
documentation is at <http://localhost:8000/docs>.

### Credentials

Secrets live in `.env` at the repository root, which is git-ignored. The committed
`.env.example` contains placeholders only and no real values.

**The current build reads no credentials and makes no model calls.** The model provider is
deliberately unset until API access is confirmed, and the application starts and runs without a
key.

**Running without a key, later.** The application will support an offline mode that replays
recorded fixture responses, so the interface and the advisory flow can be reviewed without
credentials. Fixture output is labelled as sample data in the interface, and a failed live model
call is never silently replaced by a fixture.

**Demonstration data is fictional.** No employer data, no real operational data, no BlueCallom
platform access.

---

## Scope boundaries

Out of scope for the initial build: hosting and deployment, Docker, authentication,
multi-tenancy, a database, PDF export, and integration with BlueCallom's GPTBlue platform.

---

## How this repository is produced

This is an AI-assisted project and does not pretend otherwise.

- **ChatGPT** supported requirements analysis and the preparation of the development prompts.
- **Claude**, through Claude Code, performs implementation and documentation under the project
  owner's direction.
- The project owner sets direction, reviews every stage and makes all product decisions.

Every development instruction is recorded verbatim and in order in
[docs/prompts/](docs/prompts/), and the actual outcome of each is recorded in
[docs/worklog.md](docs/worklog.md). Nothing in that record is reconstructed after the fact.
