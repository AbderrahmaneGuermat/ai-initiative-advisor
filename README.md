# AI Initiative Advisor

A strategy-consulting application for managers, built following BlueCallom's
Intelligence-over-Code (IoC) method. A manager describes their organisation, objectives,
constraints and candidate AI initiatives. The advisor reads the brief, asks up to three questions
that would change the answer, compares the initiatives qualitatively with facts, assumptions and
unknowns kept apart, and recommends where to start, with first actions and the open questions
still to confirm.

The advisory judgement lives in runtime prompt files; Python enforces schemas, limits and state.
If the manager changes the brief after advice is given, the application does not revise that
advice: it withdraws it from view and asks for a new advisory session, started deliberately.

**Assessors: start with [docs/reviewer-guide.md](docs/reviewer-guide.md).**

---

## Assessment scope

| Part | What it asks | Where |
|---|---|---|
| 1 | One application the candidate built previously | **Supplied separately.** Not this repository |
| 2 | A strategy-consulting application for managers using the IoC method | This repository |
| 3 | A sample enterprise AI interface, with the UI/UX decisions explained | This repository's interface, explained in [docs/ui-ux.md](docs/ui-ux.md) |

This application was built specifically for the assessment, starting on 2026-09-18. It is not
evidence of earlier professional work.

---

## What is where

| Path | Contents |
|---|---|
| [docs/reviewer-guide.md](docs/reviewer-guide.md) | A guided route through the application, the prompts and the evidence |
| [backend/prompts/](backend/prompts/) | **Runtime prompts**: what the application executes. The product's judgement |
| [docs/prompts/](docs/prompts/) | **Development prompts**: the instructions used to build it, verbatim and in order |
| [docs/ui-ux.md](docs/ui-ux.md) | Interface rationale for part 3 |
| [docs/architecture.md](docs/architecture.md) | How it is built, and what code owns versus what prompts own |
| [docs/requirements.md](docs/requirements.md) | The assessment, what BlueCallom states, and our interpretation |
| [docs/decisions.md](docs/decisions.md) | Decision record, including corrected and superseded decisions |
| [docs/worklog.md](docs/worklog.md) | What was done, checked and found, per development prompt |

---

## Install and run

**Tested on Windows 11** with Node.js 24.17.0, npm 11.13.0 and Python 3.14.5. Use Node 24 as the
baseline; other versions were not tested. Commands for macOS and Linux are given for convenience
but **were not run**.

### 1. Clone

```powershell
git clone https://github.com/AbderrahmaneGuermat/ai-initiative-advisor.git
cd ai-initiative-advisor
```

### 2. Install

Windows (PowerShell), from the repository root:

```powershell
npm install
python -m venv backend\.venv
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

macOS and Linux (untested):

```bash
npm install
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
```

`npm install` also installs the frontend, which is an npm workspace. The virtual environment does
not need activating; the startup script finds its interpreter.

### 3. Configure an OpenAI key

Needed only for live advice. The interface, the brief editor and all tests work without one.

Create `.env` from the example **without overwriting one you already have**:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

```bash
[ -e .env ] || cp .env.example .env     # macOS / Linux, untested
```

Open `.env` and replace `your-openai-api-key-here` with your own key from
<https://platform.openai.com/api-keys>. `.env` is git-ignored; never commit it or paste the key
anywhere else. The key is never returned by an endpoint, logged, or sent to the browser.

Two things to know:

- **The "Ready" status only means a key is present locally.** It does not authenticate it. The
  first advisory request is what proves the key works; a bad key produces a distinct
  authentication error then.
- **Live advisory sessions call the OpenAI API and may incur charges on your account.** The
  recorded sessions on the sample brief used 8 to 14 requests and were estimated at $0.026 to
  $0.086 each with `gpt-5-mini` at the rates published at the time. Those are single observations,
  not a guarantee; `GET /api/sessions/{id}/trace` reports what a session actually used.

### 4. Start

```powershell
npm run dev
```

This starts the backend on `127.0.0.1:8000` and the interface on port 5173, and stops both if
either fails. Open **<http://localhost:5173>**. (On the Windows machine used for development the
dev server listened on IPv6 only, so `localhost` worked and `127.0.0.1:5173` did not; use the
address the dev server prints.) Restart after editing `.env`; it is read once at startup.

### 5. Use it

1. The fictional Larkfield Regional Freight brief is summarised in the sidebar.
2. **Review or edit the full brief** opens an editor in the main column. It works on a draft:
   **Cancel and return** discards it; **Apply changes** keeps it. Editing never calls the advisor.
3. **Start advisory session.** A turn can take a minute or more.
4. Answer, skip, or leave blank the questions it asks, then **Send answers**. If the advisor pauses,
   select **Continue**.
5. Read the **Decision overview**, then **Reasoning & sources**.

The [reviewer guide](docs/reviewer-guide.md) walks through this with the questions a recorded run
actually asked.

---

## Inspecting a session

- **In the interface.** The decision overview shows the recommendation, its conditions, first
  actions and the questions still open. **Evidence & sources** lists what each recommendation
  cites, with identifiers. **Reasoning & sources** shows the diagnosis, the full comparison
  (facts, assumptions, unknowns, constraints, trade-offs), risks and confidence.
- **By URL.** A session writes its identifier into the address bar (`?session=<id>`). Reopening
  that link shows it again with one `GET`, running nothing. Sessions live in the backend's memory,
  so this works only until the backend restarts.
- **Through the API.** `GET /api/sessions/{id}` returns the session;
  `GET /api/sessions/{id}/trace` returns every provider attempt with prompt versions, content
  hashes and token usage; `GET /api/diagnostics` shows configuration presence, loaded prompts and
  permitted actions; `GET /api/health` shows whether a key is present. Interactive API
  documentation is at <http://localhost:8000/docs>.

---

## Tests

None of these needs a key or the network.

```powershell
backend\.venv\Scripts\python.exe -m pytest backend    # backend
npm run check:frontend                                # frontend type check
npm run build                                         # frontend production build
npm --prefix frontend test                            # frontend unit tests
```

The frontend unit tests import TypeScript directly, which relies on Node's built-in type
stripping. They were run on Node 24.17.0. The application itself does not need that feature.

At revision `d55e12f`, recorded in the worklog entry for prompt 015: **169 backend tests and 15
frontend tests passed**, with the type check and build passing. Backend tests use deterministic
test doubles in place of the model; they check contracts, limits, state and failure handling, not
the quality of the model's judgement.

---

## What was verified

**Live runs against OpenAI** (`gpt-5-mini`, fictional data), as recorded in
[docs/worklog.md](docs/worklog.md). Each is one execution; model output varies between runs.

| Session | Driven by | Notes | Requests | Tokens | Est. cost |
|---|---|---|---|---|---|
| `e0f72bc44dfb` | API | First run. 2 invalid outputs repaired; one turn cut off by the 180 s deadline then in force | 14 | 84,287 | $0.086, a floor |
| `08624152de60` | API | After corrections; 108 s of model time | 8 | 40,478 | $0.027 |
| not recorded | browser | First browser walkthrough; payloads were not saved | — | — | — |
| `40879adc7c67` | browser | Staffing answer internally inconsistent: stated about 1.5 FTE, components add to 0.7. The advisor did not notice | 8 | 40,079 | $0.026 |
| `2a60d8040351` | browser; final turn sent through the API with the same request as the Continue button | **The coherent demonstration.** 0.7 FTE entered in the brief; 0.7 appears 9 times in the advice, 1.5 never. Later reopened in the browser by URL | 9 | 46,679 | $0.027 |

**The 0.7 FTE demonstration is separate from the 1.5 FTE example.** Correcting the demonstration
data fixed what the advisor was given. It did **not** improve contradiction detection: the advisor
still does not reconcile numbers inside a manager's own answer.

**Browser checks** of the finished interface were scripted with Playwright in Chromium at
1366 × 768, 1440 × 900 and 390 × 844. They reopened the existing session `2a60d8040351` or used
prepared states (the live session's payload with status fields changed, served to the page). They
show rendering and interaction, not model behaviour, and made no model calls. Screenshots are kept
outside the repository.

**One request is unexplained.** During prompt 013 the development backend logged a
`POST /api/sessions` that none of the verification scripts made, probably from another open
browser tab. Whether it led to model requests, and at what cost, cannot be determined from the
logs.

---

## Limitations

- Sessions are held in memory and lost when the backend restarts.
- No revision within a session. A changed brief requires a new session.
- No export of the advice.
- No offline mode: every advisory step needs a live model call.
- No hosting, no Docker, no authentication, no database.
- No screen-reader verification, and no hands-on use by a person beyond scripted checks.
- Tested on Windows only.
- The advisor does not check arithmetic inside the manager's own input.

---

## Method, in brief

BlueCallom's page states that **"Prompt is King"** and **"Code is a subordinate of the King,"** and
that IoC **"has nothing to do with 'No-Code'."** It also publishes a prompt structure (role,
inputs, expected outputs, constraints) and a procedure in which ChatGPT drafts the prompts and they
are then built into an agent in GPTBlue Studio. Source:
<https://bluecallom.com/intelligence-over-code-method/>

This is a standalone application. It does not use GPTBlue Studio or any BlueCallom platform. Our
interpretation:

- **Prompts decide.** The next action, what is wrong with the brief, which questions matter, how
  the options compare and what to recommend. Each runtime prompt declares its role, inputs, outputs
  and constraints in front matter, following BlueCallom's structure.
- **Code enforces.** Schema validation, execution limits, state integrity and the set of permitted
  actions. The BlueCallom page does not ask for these; they are our engineering choices, and none of
  them decides which initiative is better.

Details: [docs/requirements.md](docs/requirements.md), section B, and
[docs/reviewer-guide.md](docs/reviewer-guide.md).

---

## How this repository was produced

This is an AI-assisted project and does not pretend otherwise.

- **The project owner** set direction, made the product decisions, reviewed each stage and wrote
  the development instructions.
- **ChatGPT** supported requirements analysis and the preparation of those instructions.
- **Claude, through Claude Code,** implemented the application and wrote the documentation under
  the project owner's direction.

Every development instruction is recorded verbatim in [docs/prompts/](docs/prompts/), and its
outcome in [docs/worklog.md](docs/worklog.md). The demonstration data is fictional. No employer
data, real operational data or BlueCallom platform access was used.
