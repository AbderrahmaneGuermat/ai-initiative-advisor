# AI Initiative Advisor

A strategy-consulting application for managers, built according to BlueCallom's
Intelligence-over-Code method. It helps a manager prioritise a portfolio of candidate enterprise
AI initiatives against their objectives, resources and constraints.

The application diagnoses the brief, asks the clarification questions that actually change the
answer, compares the alternatives, gives a justified recommendation, and revises that
recommendation when a constraint changes.

Working name. Final naming is open, see decision D2 in [docs/requirements.md](docs/requirements.md).

---

## Current status

**Design phase. No application code exists yet.**

Completed so far:

- Repository initialised, documentation structure created.
- BlueCallom's published Intelligence-over-Code material reviewed and summarised, with its stated
  requirements separated from our own implementation choices.
- Requirements, architecture and decisions documented and awaiting review.

Not started: backend, frontend, runtime prompts, demonstration data, tests, `.env.example`.

Eight decisions are open and need the project owner's input before implementation begins. They
are listed in [docs/requirements.md](docs/requirements.md), section D.

---

## What is where

| Path | Contents |
|---|---|
| [docs/requirements.md](docs/requirements.md) | Assessment requirements, what BlueCallom states, our choices, open decisions |
| [docs/architecture.md](docs/architecture.md) | Proposed architecture, responsibilities, technology rationale |
| [docs/decisions.md](docs/decisions.md) | Decision record with rationale and rejected alternatives |
| [docs/worklog.md](docs/worklog.md) | What was actually done, what was checked, what is unresolved |
| [docs/prompts/](docs/prompts/) | Chronological record of the development instructions, verbatim |

Two distinct kinds of prompt live in this repository and are deliberately kept apart.
`docs/prompts/` records the instructions used to build the software. `backend/prompts/`, once it
exists, will contain the prompts the software itself executes at runtime. The first explains how
this was made. The second is the product.

---

## Planned local execution

Not yet available. This section describes the intended experience once implementation begins, so
that the plan can be reviewed now.

**Prerequisites:** Node.js 20 or later, Python 3.11 or later, Git.

**First-time setup:**

```bash
git clone <repository-url>
cd <repository>

npm install

python -m venv backend/.venv
# Windows:        backend\.venv\Scripts\activate
# macOS / Linux:  source backend/.venv/bin/activate
pip install -r backend/requirements.txt

cp .env.example .env    # then edit
```

**Every time after that, one command from the repository root:**

```bash
npm run dev
```

This starts the FastAPI backend on port 8000 and the Vite frontend on port 5173, and opens the
interface. The frontend proxies API calls to the backend, so no CORS setup is needed.

**Credentials.** The application needs one model provider API key. It goes in `.env`, which is
git-ignored and must never be committed. `.env.example` will list every required variable with an
explanatory comment and no real values.

**Running without a key.** The application is planned to support an offline mode that replays
recorded model responses, so the interface and the full advisory flow can be reviewed without
credentials, budget or network access. See decision D-008 in [docs/decisions.md](docs/decisions.md).

**Demonstration data is fictional.** Three invented organisations. No employer data, no
BlueCallom platform access, no customer material.

---

## Scope boundaries

Out of scope for the initial build: hosting and deployment, Docker, authentication,
multi-tenancy, a database, PDF export, and integration with BlueCallom's GPTBlue platform.

---

## How this repository is being produced

This is an AI-assisted project and does not pretend otherwise.

- **ChatGPT** supported requirements analysis and the preparation of the development prompts.
- **Claude**, through Claude Code, performs implementation and documentation under the project
  owner's direction.
- The project owner sets direction, reviews every stage and makes all product decisions.

Every development instruction is recorded verbatim and in order in
[docs/prompts/](docs/prompts/), and the actual outcome of each is recorded in
[docs/worklog.md](docs/worklog.md). Nothing in that record is reconstructed after the fact.

---

## Assessment context

Built for a BlueCallom Enterprise AI Application Developer assessment, which asks for a strategy
consulting application for managers built with the Intelligence-over-Code method, an explanation
of the prompts used to develop it, and a sample enterprise AI interface with its UI/UX rationale.
All three are addressed through this single project.

Reference: <https://bluecallom.com/intelligence-over-code-method/>
