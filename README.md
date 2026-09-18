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

**Design corrected and agreed in outline. Project skeleton not yet implemented.**

Completed:

- Repository initialised, documentation structure created.
- BlueCallom's published Intelligence-over-Code page reviewed and re-verified, with its stated
  positions separated from our own interpretation.
- Requirements, architecture and decisions documented, then revised after design review.

Not started: backend application logic, runtime prompts, model integration, comparison output,
demonstration scenarios, tests, and the UI/UX rationale document.

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

## Planned local execution

Not yet available. Described here so the plan can be reviewed.

**Prerequisites:** Node.js 20 or later, Python 3.11 or later, Git.

After a one-time setup, a single command from the repository root will start both processes:

```
npm run dev
```

Credentials will live in a git-ignored `.env`. A committed `.env.example` will list every
variable as a placeholder, with no real values.

**Running without a key.** The application will support an offline mode that replays recorded
fixture responses, so the interface and the advisory flow can be reviewed without credentials.
Fixture output is labelled as sample data in the interface, and a failed live model call is never
silently replaced by a fixture.

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
