# Worklog

A factual record of work done, checks performed and issues left open. Entries are appended, never
rewritten. Nothing is recorded here that did not actually happen.

---

## 2026-09-18 — Prompt [001](prompts/001-project-brief.md), project brief

**Instruction:** Organise the repository, document requirements, propose an implementation plan.
Do not implement the application. Review BlueCallom's Intelligence-over-Code method first.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

### Work completed

1. Inspected the working directory. It was empty and was not a Git repository. Nothing existed to
   preserve.
2. Initialised a Git repository.
3. Reviewed BlueCallom's published material on the method:
   - <https://bluecallom.com/intelligence-over-code-method/> — retrieved successfully. Source of
     the "Prompt is King" hierarchy and the stated division between prompts and code.
   - <https://bluecallom.com/new-agentic-ai-framework/> — retrieved successfully. Source of the
     three-to-twenty prompts per agent figure, the Agentic Spin, and Human Interaction Points.
   - A web search was used to locate additional pages and to corroborate the statement that IoC
     is not no-code.
4. Created the documentation set: `README.md`, `docs/requirements.md`, `docs/architecture.md`,
   `docs/decisions.md`, `docs/worklog.md`, `docs/prompts/`.
5. Saved the project brief verbatim as
   [docs/prompts/001-project-brief.md](prompts/001-project-brief.md).
6. Added `.gitignore` covering Python, Node and environment files, so that `.env` cannot be
   committed once it exists.
7. Made the initial commit.

### Checks performed

- Confirmed the working directory was empty before initialising Git, so no existing work was at
  risk.
- Confirmed the saved brief in prompt 001 matches the instruction as received, with only a
  metadata header added above a horizontal rule.
- Confirmed every claim attributed to BlueCallom in `docs/requirements.md` section B traces to a
  page that was actually retrieved in this session, and recorded the source URL beside it.
- Confirmed `.gitignore` excludes `.env` and both dependency directories before committing.

No tests were run and no application code was written, because none exists. No functional
verification of any kind has taken place.

### Issues and observations

1. **One source page was unavailable.** `https://bluecallom.com/prompt-over-code-method/` returned
   HTTP 404 on direct retrieval, although it appears in search results under that URL. Its content
   was corroborated through search result extracts rather than direct retrieval. The material
   sourced this way is the "not no-code" statement in requirements B4. It is flagged here rather
   than presented as a verified direct quotation from a page we loaded.
2. **BlueCallom does not publish a development lifecycle.** The public pages give a philosophy and
   a component vocabulary, not a procedure, a prompt file format or a reference architecture.
   Everything at that level in this repository is our own choice and is labelled as such in
   requirements section C. This is stated so that no one later mistakes our conventions for
   BlueCallom's requirements.
3. **Eight decisions are open** and block the start of implementation. They are tabulated as D1
   to D8 in [requirements.md](requirements.md), section D. The two that most affect the shape of
   the code are D1, the model provider, and D4, offline mode.
4. **A design risk is recorded, not yet mitigated.** The characteristic failure of an
   Intelligence-over-Code project is a codebase that claims prompt primacy while business rules
   accumulate in Python conditionals. Acceptance criterion C7.1 exists as the test for this, and
   it cannot be exercised until code exists.
5. **Latency and cost are unestimated.** Five sequential model calls per session may be too slow
   for a comfortable demonstration. This will be measured once the pipeline runs. It has not been
   guessed at in the architecture document.

### Status at end of entry

Design documented. Implementation not started, as instructed. Awaiting the project owner's review
of the plan and answers to the open decisions.

---

## 2026-09-18 — Prompt [002](prompts/002-design-review-and-skeleton.md), design review and skeleton

**Instruction:** Correct the design documentation on six points, then implement the project
skeleton only. Verify what can be verified and report what cannot.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

This entry is written in two parts, because the instruction asked for two separate commits.

### Part A — documentation corrections

1. Re-retrieved <https://bluecallom.com/intelligence-over-code-method/> and queried it
   specifically for statements about prompts, code, no-code, orchestration, control mechanisms and
   claimed benefits.
2. Rewrote `docs/requirements.md`:
   - Assessment scope restated. This repository addresses parts 2 and 3 only. Part 1 is the
     project owner's prior professional work and is handled separately. Added an explicit
     statement that this application is newly built and is not evidence of earlier work.
   - Section B now cites the single working source URL throughout.
   - Replaced the fixed five-stage pipeline with advisory actions chosen per turn.
   - Added the code-enforced controls, labelled as our engineering judgement.
   - Replaced weighted scoring with the five-category qualitative comparison.
   - Added the maximum of three clarification questions and the rule that skipped answers stay
     visible as unknowns or labelled assumptions.
   - Recorded the confirmed choices and the decisions that remain open.
3. Rewrote `docs/architecture.md`: bounded advisory loop with a fixed action contract, the four
   guards, the comparison model with no numeric default path, and technology rationale restated on
   suitability and maintainability.
4. Rewrote `docs/decisions.md`: superseded entries kept with their replacements named, rather than
   deleted.
5. Rewrote `README.md`: scope, status, and a short account of the method.
6. Saved prompt 002 verbatim and added it to the prompt index.

### Checks performed, Part A

- Confirmed every statement attributed to BlueCallom in requirements section B comes from the
  single page retrieved in this session, and that the page was reachable at the time of writing.
- **Correction to the previous entry.** The 2026-09-18 entry for prompt 001 recorded that the
  "not no-code" statement had been corroborated only through search extracts, because
  `bluecallom.com/prompt-over-code-method/` returned HTTP 404. On re-checking, that statement
  appears on the working method page itself, and it is now quoted and cited from there. The
  earlier entry is left unedited, as the worklog is append-only. The 404 page is no longer cited
  anywhere in the documentation.
- **Verified a negative and recorded it.** The source page makes no mention of testing,
  validation, schemas, execution limits or control mechanisms. This is stated in requirements B7,
  so that the controls this project adds are not mistaken for BlueCallom requirements.
- Confirmed no document presents the application as prior professional experience.
- Confirmed the previous claim that TypeScript or a component library conflicts with IoC has been
  withdrawn and corrected, in architecture section 6 and decision D-006a.

### Issues, Part A

1. The revised design has not been validated against running advisory code, because none exists.
   In particular the claim that a bounded adaptive loop is workable within acceptable latency is
   untested.
2. Five decisions remain open: model provider, session persistence, export formats, test depth and
   streaming. Only the provider was explicitly deferred by the project owner; the other four carry
   recommendations awaiting a decision.

### Part B — skeleton implementation

Built, per the instruction, the structure and nothing more.

1. **Root tooling.** `package.json` declaring `frontend` as an npm workspace, so one `npm install`
   covers both. `npm run dev` runs `concurrently` over the two processes.
2. **`scripts/dev-backend.mjs`.** Locates the virtual environment interpreter at
   `backend/.venv/Scripts/python.exe` or `backend/.venv/bin/python` and starts Uvicorn. Written
   because `npm run dev` should not require the developer to activate a virtual environment first,
   and the interpreter path differs per platform. If no environment is found it prints the exact
   setup commands and exits non-zero.
3. **Backend.** `app/main.py` mounting the router under `/api`, `app/config.py` reading settings
   from the environment, and `app/api/routes.py` with `GET /api/health`. Empty `prompts/`,
   `fixtures/` and `tests/` directories are kept with placeholder files.
4. **Health endpoint honesty.** The response carries the build stage plus explicit `implemented`
   and `not_implemented` lists, so anyone calling the API can see how much of the application is
   real rather than inferring capability from a bare `"ok"`.
5. **Frontend.** Vite, React and TypeScript. A shell rendering the three proposed regions, a
   permanent "Unfinished prototype" banner, and a backend status indicator. Every region is a
   labelled placeholder marked "not implemented". No invented content that could be mistaken for
   generated advice appears anywhere.
6. **`.env.example`** with placeholders only. No credential, real or plausible.
7. **Configuration.** The model provider is unset by default. Nothing in this build reads a key or
   calls a model. The health endpoint reports whether a provider is configured as a boolean; the
   key itself is never returned, logged or sent to the frontend.
8. **Ignore rules** confirmed to cover `.env`, both dependency directories, the virtual
   environment and the build output.

### Checks performed, Part B

Everything below was actually executed in this session on Windows 11, Node 24.17.0, npm 11.13.0,
Python 3.14.5.

| Check | Result |
|---|---|
| `python -m venv backend/.venv` and pip install of `backend/requirements.txt` | Succeeded. FastAPI 0.141.1, Pydantic 2.13.5, pydantic-settings 2.15.0, Uvicorn 0.53.0, PyYAML 6.0.3 |
| `npm install` at the repository root | Succeeded, 96 packages, frontend workspace included |
| `npm run check:frontend` (`tsc --noEmit`) | Passed with no errors |
| `from app.main import app` | Imported without error |
| `npm run dev` | Both processes started. Uvicorn on 127.0.0.1:8000, Vite on port 5173 |
| `GET http://127.0.0.1:8000/api/health` | HTTP 200 with the expected JSON body |
| `GET http://localhost:5173/api/health` through the Vite proxy | HTTP 200, identical body. Frontend-to-backend path confirmed |
| Every frontend module and stylesheet requested from the dev server | All 13 returned HTTP 200, so nothing fails to transform |
| `npm run build` | Succeeded. 36 modules transformed |
| Documented Windows PowerShell setup commands, run verbatim | pip install and `Copy-Item .env.example .env` both worked |
| `git check-ignore` on `.env`, `node_modules`, `backend/.venv`, `frontend/dist` | All ignored |
| Files staged for commit | Reviewed. 29 files, no dependency directories, no build output, no `.env` |
| Both dev processes stopped afterwards | Confirmed. No listener remains on either port |

### Not verified

1. **Rendered interface in a browser.** No browser automation is available in this environment. I
   confirmed that the page is served, that every module transforms, that the type check and the
   production build pass, and that the health request succeeds through the proxy. I did **not**
   observe the rendered DOM, so the visual layout and the status indicator's on-screen appearance
   remain unconfirmed. The project owner should open <http://localhost:5173> and check.
2. **macOS and Linux.** Only the Windows branch of `scripts/dev-backend.mjs` was exercised. The
   POSIX branch is written but untested.
3. **The error path of the startup script.** The message shown when no virtual environment exists
   was not triggered, because the environment was created first.
4. **Everything related to advice.** No model call, prompt, comparison or recommendation exists to
   test. Nothing in this build produces advisory output of any kind.

### Observations

1. **Vite binds to the IPv6 loopback only.** `http://127.0.0.1:5173` refuses the connection while
   `http://localhost:5173` works. Confirmed with `netstat`, which shows the listener on `[::1]`.
   Documented in the README rather than worked around, since the backend listens on IPv4 and the
   proxy functions correctly either way.
2. **Python 3.14.5 is newer than the documented floor of 3.11.** All dependencies installed and
   ran without issue, but only 3.14.5 has actually been exercised.
3. A transcription error was introduced and corrected while editing the README: a Windows path in
   the setup block briefly lost a backslash to an escape-sequence mistake. Caught by re-reading the
   file, fixed, and the corrected commands were then executed verbatim to confirm they work.

### Status at end of entry

Documentation corrected and committed. Skeleton implemented, running and committed separately. No
remote configured and nothing pushed, as instructed. Awaiting review before the advisory loop,
runtime prompts and model integration are built.

---

## 2026-09-18 — Prompt [003](prompts/003-publish-to-github.md), publish to GitHub

**Instruction:** Publish the existing local repository to a confirmed public GitHub destination,
after verifying the authenticated account, the existing remotes and the absence of secrets. No new
features.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

### Work completed

1. Saved the instruction verbatim as
   [prompts/003-publish-to-github.md](prompts/003-publish-to-github.md) and added it to the prompt
   index, before making any change.
2. Verified the authenticated GitHub identity.
3. Inspected the local repository and its remotes.
4. Scanned every tracked file and the full commit history for credentials and confidential
   material.
5. Committed the prompt record.
6. Configured `origin` and pushed `master` with its upstream set.
7. Verified the published result against the local repository.

### Checks performed

**Authentication.** The GitHub CLI is not installed on this machine, so the identity was confirmed
through the credential helper and the GitHub API instead. Git Credential Manager holds a
credential for `github.com` under the username `AbderrahmaneGuermat`. Calling
`GET https://api.github.com/user` with that credential returned HTTP 200 and
`login: AbderrahmaneGuermat`, user id 61157096. The same credential reports `admin`, `maintain`
and `push` permissions on the destination repository. **The active account is the expected one.**

**Destination.** `AbderrahmaneGuermat/ai-initiative-advisor` existed, was public, and was empty
before the push, with a reported size of 0 and a default branch of `master`.

**Remotes before the change.** None. `git remote` listed nothing, so no existing `origin` pointed
anywhere else and nothing was reconfigured or overwritten.

**Branch.** The local branch was `master`, matching the repository's default branch. It was pushed
under its existing name. No branch was renamed, and no force-push was used.

**Secret and confidentiality scan.**

| Check | Result |
|---|---|
| Every file ever added across all commits, listed and reviewed | 38 files before this entry, all expected |
| `.env`, `.venv/`, `node_modules/` or `dist/` anywhere in history | None. Never committed at any point |
| Provider key patterns across all commits, including OpenAI, Anthropic, GitHub, AWS, Slack, PEM private keys and bearer tokens | No matches |
| Assignment-style secrets, such as a key, token, secret or password set to a long value | No matches |
| Only key-shaped line in the repository | `MODEL_API_KEY=your-api-key-here` in `.env.example`, a placeholder |
| Email addresses in tracked file contents | None |
| Named employer, client or customer in the documentation | None. Only generic references, all of which state that no such data is used |

**Publication result.**

| Check | Result |
|---|---|
| Push | `master -> master`, new branch, upstream set to `origin/master` |
| Local `master` against `origin/master` | Identical, both at `2ce503a` at the time of the push |
| `git diff master origin/master` | Empty. Trees identical |
| Commit history on the remote | All four commits present, in order, unmodified |
| File list on the remote, read back through the GitHub trees API | 39 blobs, exactly matching the 39 locally tracked files. Nothing extra, nothing missing |
| Excluded paths on the remote | None. No `.env`, no dependency directory, no build output |

### Issues and observations

1. **The GitHub CLI is not installed**, so the account verification used the credential helper and
   the GitHub REST API rather than `gh auth status`. The result is equivalent, since the token
   checked is the one Git itself uses to push, but it is worth recording that the usual tool was
   not available.
2. **Commit authorship is now public.** The three earlier commits and this one carry the author
   name `Abderrahmane` and the address `abdeguermat@gmail.com`, taken from the local Git
   configuration. This is normal for a personal repository and was not changed, but it is stated
   here because the repository is public and the address is therefore visible to anyone.
3. **No secret scanning tool was run.** The checks above are pattern searches over the repository
   and its history, performed here. They found nothing, but they are not a substitute for GitHub's
   own secret scanning, which the project owner may wish to enable on the repository settings.
4. The application itself is unchanged. It remains at the skeleton stage, and nothing about
   publication altered what the software does.

### Status at end of entry

Published to <https://github.com/AbderrahmaneGuermat/ai-initiative-advisor> on branch `master`,
with history preserved and upstream tracking configured. No features were added. Awaiting review
before the advisory loop, runtime prompts and model integration are built.

---

## 2026-09-18 — Prompt [004](prompts/004-data-contracts-and-foundations.md), data contracts and foundations

**Instruction:** Correct five documentation inconsistencies, implement the data contracts, add one
fictional worked example, test the contract boundaries. No model calls, advisory loop, persistence,
exports or frontend redesign.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

### Part A — corrections

1. **Unused configuration removed.** `BACKEND_HOST` and `BACKEND_PORT` were advertised in
   `.env.example` and declared in the settings object, but nothing read them: the address is
   hard-coded in `scripts/dev-backend.mjs`. Setting them would have changed nothing while appearing
   to. Both are deleted, and the documentation now states that the local addresses are fixed and
   where they are fixed. Recorded as D-015.
2. **IPv6 claim narrowed.** The README described the dev server binding the IPv6 loopback as
   general behaviour. It is now stated as what was observed on the one Windows 11 machine this was
   tested on, and the same correction is applied to the comment in `frontend/vite.config.ts`.
   Platform support and platforms actually tested are now distinguished.
3. **Schema overclaim corrected.** The architecture had said that separate schema fields mean "an
   assumption cannot arrive labelled as a fact." That is false: a model can put anything in any
   field and the schema accepts it if the shape is right. Corrected in the architecture, in
   requirements C5, and in decision D-003, with the reasoning recorded as D-016. The honest claim
   is narrower and still worth having: structural separation and resolvable references make a wrong
   claim findable by a reader who is not its author. They do not prevent one.
4. **Action and prompt mismatch resolved.** The architecture listed a `diagnose.md` prompt while
   the permitted action set had no `diagnose` action, which meant that prompt could never have run.
   `diagnose` is now a permitted action, and every action is bound to its output contract in one
   declaration, `ACTION_OUTPUT_CONTRACTS`. A test fails if an action is ever added without one.
   Recorded as D-017.
5. **Stack rationale corrected.** The claim that Next.js or TypeScript would blur the
   Intelligence-over-Code boundary is withdrawn from both the architecture and the decision record.
   The stack is now explained on suitability and on the project owner's familiarity, which is the
   true reason. Recorded as D-018, which also names the pattern: dressing a preference as a
   methodological requirement sounds more rigorous and is simply less true.

Historical development prompts were not edited. Corrections live in current documentation and in
new decision entries, as instructed.

### Part B — data contracts

Added under `backend/app/models/`: `common.py`, `brief.py`, `clarification.py`, `comparison.py`,
`recommendation.py`, `actions.py`, `references.py`.

Design points worth recording:

- **Explicit unknowns.** Where a value may be absent, the field is required and nullable rather
  than optional with a default. A producer has to write `null` deliberately. Nothing is filled in
  quietly.
- **No numbers anywhere.** Priority is list order plus a coarse qualitative stance. A test walks
  every output contract recursively and fails if any numeric field appears at any depth, so scoring
  cannot return under another name without someone arguing for it.
- **Three answer states.** Answered, skipped and unanswered are distinct. A skipped question is a
  decision the manager made; an unanswered one is not. Neither may carry answer text, so nothing is
  attributed to a manager who did not reply, and neither is citable as a source.
- **References are structural.** `references.py` checks that a cited identifier exists. It is a
  separate explicit call rather than a model validator, because a payload cannot see the brief it
  was produced against, and because keeping it explicit stops it being mistaken for a guarantee the
  type system provides.
- **Business judgement stayed out of validators.** No validator contains a rule about what makes an
  initiative good. An incomplete brief is valid, and a test pins that: noticing thinness is the
  advisor's job, not a validator's.

### Part C — worked example

One fictional scenario, Larkfield Regional Freight, with three candidate initiatives and a
deliberately incomplete brief: an objective with no rationale, a constraint naming a kind with no
value, and an initiative with a name and no description.

Four example payloads run in sequence against it: a clarification round with one answered, one
skipped and one untouched question; a comparison; a recommendation; and a revision after the budget
is cut. All are labelled as hand-authored fiction in the files themselves and in
`backend/app/data/README.md`, which states explicitly that they are not recorded model responses,
not offline fixtures, and not evidence that the advisor works.

The example carries the design property the qualitative approach exists to produce, and a test pins
it: the question the manager skipped becomes an entry under missing evidence for the initiative it
affects, and is carried forward into both the recommendation and the revision. It never becomes a
low rating.

### Checks performed

All executed in this session on Windows 11, Python 3.14.5.

| Check | Result |
|---|---|
| `pytest backend` | **44 passed**, 0 failed, in 0.35s |
| Tests run from the repository root and from `backend/` | Both pass, after adding `backend/pytest.ini` |
| Unknown advisory action rejected | Passes |
| Batch of four clarification questions rejected; three accepted | Passes |
| Answered question with no answer, and skipped question carrying text, both rejected | Passes |
| Unanswered question dropped from a round, rejected | Passes |
| Unresolvable source reference detected | Passes |
| Reference to a skipped answer does not resolve | Passes |
| Recommendation naming an initiative absent from the brief, detected | Passes |
| Every action has a declared output contract | Passes |
| No numeric field anywhere in any output contract, at any depth | Passes |
| All five example payloads validate, and every reference resolves | Passes |
| Backend imports and serves after the configuration change | HTTP 200 on `/api/health` and `/openapi.json` |
| Health endpoint reports the new stage | `data-contracts`, with implemented and not-implemented lists updated |

### Issues and observations

1. **A test gave a false failure on its first run**, and the cause is worth recording. The
   numeric-field check originally searched the *string* form of each annotation for `int`, which
   matched the substring inside `StringConstraints`. It reported four fields that hold no numbers
   at all. Rewritten to walk annotations structurally with `typing.get_args`, recursing into nested
   models, and exempting enums and booleans. The lesson is ordinary and worth keeping: a check that
   greps a repr is not a check.
2. **The health endpoint was updated but the frontend was not.** The interface reports whatever
   stage the backend gives it, so it now displays `data-contracts`, but no frontend work was done
   in this iteration and none was asked for.
3. **`TestClient` could not be used.** Starlette's test client requires `httpx`, which is not a
   dependency. Rather than add one for a single check, the backend was verified by running Uvicorn
   and issuing real HTTP requests. That is a better check in itself, but it means the suite
   contains no in-process API test.
4. **What the tests do not establish.** They confirm shape and referential integrity. They do not
   confirm that the example analysis is sound, that a claim filed under stated facts is a fact, or
   that a citation supports the claim citing it. Two tests exist specifically to pin that limit,
   including one where a real reference supports a nonsensical claim and passes deliberately.
5. **Still nothing produces advice.** No model integration, no runtime prompts, no advisory loop,
   no persistence, no exports. The contracts describe a conversation the application cannot yet
   have.
6. **The prompt files named in `ACTION_PROMPTS` do not exist.** The mapping declares the paths that
   `backend/prompts/` will hold. Nothing loads them yet, so a wrong path there would not currently
   fail anything.

### Status at end of entry

Corrections applied, contracts implemented and tested, one worked example validated. Committed and
pushed to the confirmed repository. Awaiting review before runtime prompts, the model client and
the advisory loop are built.

---

## 2026-09-18 — Prompt [005](prompts/005-openai-advisory-flow.md), OpenAI integration and the first advisory flow

**Instruction:** Integrate OpenAI, implement the runtime prompts and a bounded advisory loop, add a
single validation boundary, wire the interface, and verify with deterministic doubles.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

### The finding that shaped the iteration

Before writing any adapter, the existing contracts were checked against the SDK's own strict-schema
converter. **Every one of them emitted at least one keyword Structured Outputs does not support**:

| Contract | Unsupported keywords present |
|---|---|
| NextAction | minLength |
| Diagnosis | minLength, default |
| ContextRequest | minLength, minItems |
| ClarificationBatch | minLength, pattern, minItems, maxItems, default |
| Comparison | minLength, pattern, minItems, default |
| Recommendation | minLength, pattern, minItems, default |
| Revision | minLength, pattern, minItems, default |

Sending them would have meant either a rejected schema or constraints silently dropped. The answer
was a separate wire layer, `app/models/wire.py`, compatible by construction, with the strict
contracts applied afterwards in the validation boundary. Recorded as D-019. A check confirms all
sixteen wire models convert with zero unsupported keywords.

### What was built

**OpenAI integration.** Async SDK, Responses API, `responses.parse` with a Pydantic wire model as
`text_format`. Default `gpt-5-mini`, configurable, never switched by the application. SDK retries
disabled so no request escapes the budget. Missing credentials, authentication, rate limits,
timeouts, connection loss, rejected requests, refusals and truncated output each map to a named
exception carrying whether a retry could help.

**Runtime prompts.** Eight files under `backend/prompts/`, each with front matter declaring
identifier, version, role, inputs, outputs and constraints. Read from disk **on every execution**,
never cached, with a SHA-256 content hash recorded in the session trace.

**The advisory loop.** The next-action prompt chooses; Python fixes the permitted set, the
prerequisites, the ceilings and whether output may be kept. `await_user` makes no model call.
Limits cover actions, requests, input size and wall-clock time, and the request budget counts
selector and repair calls, so it cannot be gamed.

**The validation boundary.** One entry point. Contract, context identity, references, question
status, prior outputs, revision snapshots. Two review findings closed, both with regression tests.

**Interface.** The three panels now work: load and edit the brief, start a session, answer or skip
questions, see the comparison and recommendation, see loading and recoverable errors. Open
questions render from session state rather than from the advice text.

**Worked examples corrected.** The revision example claimed route optimisation "cannot be done
properly" at 60,000 EUR. No cost estimate exists for any option in that scenario, so the budget
establishes nothing about feasibility. Rewritten so the stance change rests on the shrinking margin
for being wrong about an unestimated cost, and a new open unknown names the missing estimates
directly. Their attribution as hand-authored fiction is unchanged.

### Checks performed

All executed in this session on Windows 11, Python 3.14.5, openai SDK 3.16.1.

| Check | Result |
|---|---|
| `pytest backend` | **108 passed**, 0 failed |
| Wire schema compatibility, all 16 models | All convert with zero unsupported keywords |
| Frontend `tsc --noEmit` | Passed |
| `npm run build` | Passed, 35 modules |
| Backend imports; all 8 prompts load with valid front matter | Passed |
| Full flow: diagnose, clarify, pause, answer, compare, recommend | Passed, via the API with a double |
| `await_user` makes no second model call | Passed, one request recorded |
| Repair: one attempt, succeeds | Passed |
| Repair: second failure stops, commits nothing, exactly three requests | Passed |
| Invalid output does not replace previously validated advice | Passed |
| Request, action and input-size limits stop the loop | Passed |
| Provider failures surface and commit nothing, four kinds | Passed |
| Unrelated context identifier rejected | Passed, regression |
| Revision with a nonexistent constraint rejected | Passed, regression |
| Revision with misreported values rejected | Passed |
| Skipped question: preserved, not re-askable, not citable | Passed |
| Four-question batch valid on the wire, rejected by the contract | Passed |
| Prompt edits reach the adapter without a restart | Passed, asserted on instructions actually sent |
| Manager text fenced; delimiter injection neutralised | Passed |
| App starts and serves health and scenario with no credentials | Passed |

### Live verification: PENDING

**No request has been made to OpenAI.** No API key was present in this environment, so the smoke
test could not run. Every test above uses deterministic doubles.

What that means precisely: the integration is complete, the schemas are confirmed compatible with
the documented Structured Outputs subset, and the failure paths are exercised. What has **not** been
observed is the real service accepting these schemas, the quality of what `gpt-5-mini` returns, real
latency, or real token cost. The README documents the smoke test to run once a key is configured.

### Issues and observations

1. **A deadlock was found by a test, not by inspection.** The first implementation blocked while any
   question was unanswered, so a manager who answered two of three and left the third alone would
   never receive advice. Blocking is now per round: once the manager submits, the round stops
   blocking and untouched questions become open unknowns. Recorded as D-023. This is also the more
   honest semantics, since leaving a field blank is itself an answer.
2. **A false test failure, worth recording.** The numeric-field guard from the previous iteration
   had searched annotation reprs for `int`, matching the substring inside `StringConstraints`. It
   was rewritten to walk types structurally. Mentioned again because it is the same class of
   mistake as trusting the API to enforce our constraints: checking the appearance of a thing
   rather than the thing.
3. **Prompt quality is untested.** Nothing here establishes that the prompts elicit good advice.
   The doubles return whatever the test scripted. Only a live run with a person reading the output
   can judge that, and it has not happened.
4. **`revise` is validated but not offered.** Its contract and checks exist and are tested. Its user
   flow does not, so it is excluded from the advertised action set rather than left available to be
   chosen and then fail.
5. **Sessions are lost on restart.** In-memory only, stated in three places.
6. **No in-process API test existed before this iteration** because `httpx` was absent. It is now a
   dependency and `tests/test_api.py` exercises the HTTP surface end to end.
7. **Adding or removing brief items is not implemented.** Existing objectives, constraints and
   initiatives can be edited; the lists themselves are fixed to what the scenario provides.

### Status at end of entry

The advisory flow works against deterministic doubles and is ready for a live smoke test. Committed
and pushed. Awaiting the project owner's live run and review.

---

## 2026-09-18 — Prompt [006](prompts/006-live-test-readiness.md), live test readiness

**Instruction:** Fix five findings raised against commit `a19dce9` before the first live test. No
new features.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

### What was wrong, and what was done

**1. Configuration status accepted the committed placeholder.** `Settings.model_configured`
returned true for any non-empty provider and key, so copying `.env.example` without editing it
reported the advisor as ready. Replaced with one check in `app/core/configuration.py`, shared by the
health endpoint and client construction, rejecting empty values, an explicit placeholder list and
providers with no adapter. No format rule is imposed on the key. The field is renamed
`model_configured_locally` and every response carries a note saying it is not authentication.
Recorded as D-024.

**2. The turn deadline could be crossed in flight.** `check_time()` ran only between iterations, so
a slow request could overrun the limit and still commit. The remaining budget now bounds each
awaited call through `asyncio.wait_for`, and is re-checked before anything is committed. Cancelled
and late results are recorded and discarded. `finally` guarantees the status returns to ready and
the lock is released. Recorded as D-025.

**3. The execution trace was lost.** `TurnResult.traces` was never persisted and the trace endpoint
read only accepted outputs, so selector calls, repair costs and failed requests left no record.
Added `session.attempts`, append-only, written as each attempt completes so successful ones survive
a later failure. Usage is reported only where the provider gave it, with `usage_available` explicit.
Clarification records now carry their prompt trace and usage, which they previously lacked entirely.
Recorded as D-026.

**4. Answers were written outside the session lock.** A submission could modify answers while a turn
was awaiting a model response, so advice could be generated against one set and committed against
another. `run_turn` now takes a `prepare` callable executed inside the lock. One lock, nothing
nested, no deadlock available. Recorded as D-027.

**5. The schema claim was too broad.** See below.

### The schema documentation, and what could not be verified

The official guide at <https://developers.openai.com/api/docs/guides/structured-outputs> was
retrieved three times in this session, including with an anchored URL. **Every retrieval truncated
before the supported-schemas section**, ending mid-sentence in "Tips and best practices". A targeted
search of the returned content for "fine-tuned", "additional restrictions", "minLength", "pattern"
and "minItems" found none of them present. A web search returned only third-party summaries, which
disagreed with each other.

So the per-keyword support list **could not be verified from the official source here**, and this
entry says so rather than implying otherwise. The project owner's statement that the documentation
distinguishes additional restrictions for fine-tuned models is recorded as their report, attributed
to them.

The previous blanket claim is withdrawn. The wire layer stays, rejustified: it is a deliberately
conservative subset we chose, not a description of what the service rejects. Three things are now
kept apart in the documentation and in the module docstring: our chosen subset, local conversion
checks, and actual service acceptance. **Only the first two have been established. No request has
ever been made to OpenAI.** Recorded as D-028.

### Checks performed

All executed in this session on Windows 11, Python 3.14.5.

| Check | Result |
|---|---|
| `pytest backend` | **133 passed**, 0 failed (was 108) |
| Frontend `tsc --noEmit` and `npm run build` | Both pass |
| Committed placeholder rejected, in the running app | `configured_locally: false`, with the placeholder named |
| Session refused with the placeholder | HTTP 503, `ModelNotConfigured`, problem listed |
| An unusual-format key accepted, in the running app | `configured_locally: true`, no problems |
| Health check and client construction agree | Same function, asserted |
| In-flight deadline overrun cancelled | Passes, and completes in under 2s rather than waiting 5s |
| Nothing committed after an overrun; session usable; lock released | Passes |
| Cancelled request recorded with no invented usage | Passes |
| Selector calls recorded with prompt hash and usage | Passes |
| Repair records both attempts, each with its own usage | Passes |
| Clarification record carries provenance and usage | Passes |
| Completed attempts survive a later failure in the same turn | Passes |
| Answers cannot be applied while a turn is in flight | Passes, observed from inside the call |
| Refused submission consumes no turn and leaves the lock free | Passes |
| Two concurrent turns do not interleave | Passes |

### Issues and observations

1. **A stale process nearly produced a false verification.** The first end-to-end check returned the
   old health shape. The cause was a backend left listening on port 8000 from an earlier run, which
   the new dev server could not replace; `pkill -f uvicorn` had not matched it on Windows. The
   servers were killed by PID and the check re-run. Worth recording because the failure mode looked
   like a code defect and was not: a green check against a stale process is worse than a red one.
2. **`.env` is read once at startup.** Editing it while the backend runs changes nothing, because
   the file sits outside the reload watch directory. The README now says to restart after editing.
3. **A small accounting fix.** The request counter was incremented before the deadline check, so a
   request that was never sent could be charged. Reordered.
4. **Live verification remains pending.** No API key was available, so nothing in this iteration
   made a request to OpenAI. Prompt quality, real latency, real cost and whether the service accepts
   these schemas are all still unobserved.

### Status at end of entry

The five findings are fixed and covered by regression tests. Committed and pushed. The project owner
will configure a key locally and run the first live user-flow test; **live verification stays marked
pending until that actually happens.**

---

## 2026-09-18 — Prompt [007](prompts/007-live-run-corrections.md), the first live runs and what they changed

**Instruction:** Record the first real run, correct the timeout message and continuity, fix the
skipped-question references, improve the advisor's sequencing, measure reasoning and cached tokens,
and run one follow-up test. No new features.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

---

### Part A — the first live run, recorded

**This section describes real requests to OpenAI.** Everything in every previous worklog entry was
produced with deterministic doubles: scripted objects returned by `tests/doubles.py`, no network, no
key. The two are not comparable and are kept apart here. The doubles establish that the machinery
behaves; only these runs establish that the service accepts what we send and that the advice is
worth reading.

**Configuration.** Provider OpenAI, model `gpt-5-mini`, Responses API with native Structured
Outputs, SDK 3.16.1, retries disabled, `max_output_tokens` 8000, turn deadline 180s, no reasoning
effort parameter sent. Prompts at version 1.0.0.

**Scenario.** The fictional Larkfield Regional Freight brief, unedited: three initiatives, an
objective with no rationale, a constraint with no value, an initiative with no description. One
question answered with a volume figure, one skipped, the rest skipped in a later round.

**What worked.** The service accepted every schema. No request was rejected for schema reasons,
which resolves the open question from D-028: the conservative wire subset is acceptable to the
service in practice, for this model. The full flow completed. Skipped questions were preserved,
surfaced in `open_unknowns` and never answered on the manager's behalf. Stated facts cited real
identifiers, assumptions carried none. No unsupported cost or feasibility claim appeared. The
deadline cancellation fired in real conditions and recorded the attempt with no invented usage.

**The numbers, with their denominators.**

| Measure | Count | Of what |
|---|---|---|
| Provider requests | 14 | all calls: 6 selector, 6 action, 2 repair |
| Action outputs returned and validated | 5 | one further action request was cancelled and returned nothing |
| Outputs rejected by validation | 2 | **2 of 5 validated outputs, 40%.** As a share of all 14 requests, 14% |
| Repair attempts | 2 | both succeeded on the first and only attempt |
| Requests cancelled by the deadline | 1 | a comparison call, cut off mid-flight |
| Turns | 4 | one of which stopped at the 180s limit |

The "40%" reported informally earlier is the rejected share of validated action outputs. It is not
a share of requests, and stating it without the denominator overstated the problem.

**Tokens and cost.** 84,287 tokens counted across the 13 requests that returned usage. At published
`gpt-5-mini` rates that is **approximately $0.086**. This is a floor rather than a total: the
cancelled request returned no usage, and a request with no usage data is not a request that cost
nothing. It was issued, the provider did work on it, and it may have been billed.

**What the run found, all four of which are fixed below.**

1. The timeout message said "Nothing partial was saved" while a validated comparison had been saved
   and kept. The message was false about the state of the session.
2. Both rejections had a single cause: the model cited skipped question identifiers as
   `clarification.answer` sources, five times across two outputs. The repairs cost roughly 23,000
   tokens, about a quarter of the session.
3. The advisor diagnosed the brief after comparing it.
4. Six questions across two rounds before any comparison.

---

### Part B — the corrections

**Timeout and continuity.** The limit message now names what completed and was saved, what was
interrupted, and what the session still holds. Only the interrupted step's output is discarded. A
comparison records the answers version it was made against, so Continue resumes from a current
comparison instead of paying for it twice. The turn deadline is now configurable and defaults to
300 seconds. **This is operational headroom, not a performance improvement**: nothing got faster,
the same work simply has room to finish in one turn. Recorded as D-029, D-030 and D-031.

**Skipped questions.** The prohibition is unchanged. What changed is the input: two separate lists,
one of answers that may be cited with their text, one of every question's status marked as
awareness only, plus two short worked examples in the prompts. Recorded as D-032.

**Sequencing.** `diagnose` is offered only while no comparison exists, and never required.
Clarification is one round by default; afterwards the advisor proceeds and records the rest as open
unknowns. The selector now receives the substance of what it has already concluded, the diagnosis
findings, the comparison criteria and its recorded unknowns per initiative, rather than booleans
saying those things exist. Recorded as D-033.

**Measurement.** Reasoning and cached input tokens are recorded where the provider reports them,
as subsets of the output and input totals respectively, never added to them. Reasoning effort
defaults to `low`. Recorded as D-034.

---

### Part C — the second live run

Same scenario, same shape of answers: one answered with the same volume figure, one skipped, one
left untouched. Prompts at 1.1.0, reasoning effort `low`, turn deadline 300s.

| Measure | First run | Second run |
|---|---|---|
| Provider requests | 14 | **8** |
| Selector / action / repair | 6 / 6 / 2 | 4 / 4 / 0 |
| Outputs rejected by validation | 2 | **0** |
| Repair attempts | 2 | **0** |
| Cancelled by the deadline | 1 | **0** |
| Clarification rounds | 2, six questions | **1, three questions** |
| Diagnosis position | after the comparison | **first** |
| Input tokens | 47,257 | 30,648 |
| Output tokens | 37,030 | 9,830 |
| of which reasoning | not measured | 2,048 |
| Cached input tokens | not measured | 0 |
| Total counted | 84,287 | **40,478** |
| Estimated cost | ~$0.086, a floor | **~$0.027** |
| Turns / wall clock | 4 turns, one hitting 180s | **2 turns, 108s** |

Every usage figure in the second run is present, so its estimate is a total rather than a floor.

**What the second run confirms.** Diagnosis ran first, of the selector's own choosing. One
clarification round. No output rejected, so the citable-answers split and the worked examples did
what they were meant to. No timeout. The advice again cites real sources, labels assumptions,
carries the skipped question into `open_unknowns` naming it as skipped, and makes no unsupported
cost claim.

**Two honest observations about it.**

1. **The order was diagnose, compare, then ask.** Comparing before asking is permitted and not
   obviously wrong, but the comparison was made before the manager's volume answer arrived. When
   the answer came, the selector went straight to `recommend` rather than re-comparing, even though
   the comparison had correctly become stale and `compare` was available. The recommendation does
   use the answer. Whether it should have re-compared first is a judgement worth watching over more
   runs, and it is the selector's to make.
2. **No cached input tokens were observed.** Every call reported zero. The assembled input differs
   per call, so there may be little for the provider to cache. Nothing is concluded from one run.

---

### Checks performed

| Check | Result |
|---|---|
| `pytest backend` | **150 passed**, 0 failed (was 133) |
| Frontend `tsc --noEmit` | Passes |
| New: timeout keeps the comparison and the message says so | Passes |
| New: timeout with nothing committed says that instead | Passes |
| New: Continue does not re-offer a current comparison | Passes |
| New: Continue reaches the recommendation with no second comparison | Passes |
| New: new answers make the comparison stale again | Passes |
| New: diagnose not offered once a comparison exists | Passes |
| New: diagnosis remains optional | Passes |
| New: one clarification round by default, configurable | Passes |
| New: citable answers exclude skipped and unanswered | Passes |
| New: the prompt separates citable answers from question status | Passes, asserted on the text sent |
| New: reasoning and cached tokens recorded without double counting | Passes |
| Second live run, end to end | Completed, 8 requests, 0 rejections |

### Issues and limitations

1. **The interface has still not been used.** Every check, live and otherwise, has gone through the
   API. Nobody has opened a browser, so the rendering, the forms, the skip control and the error
   banner are unverified. The README now has step-by-step instructions for doing it.
2. **The timeout fix was not exercised live.** The second run did not time out, which is the point,
   but it means the new recovery message has been seen only in tests.
3. **Two live runs is not a sample.** The improvements are large enough to be unlikely to be noise,
   but prompt behaviour varies and nothing here is a controlled comparison.
4. **Reasoning effort was changed at the same time as the prompts**, so the token reduction cannot
   be attributed to either alone. Both changes were wanted regardless.
5. **Cost figures are estimates** from provider-reported usage at published rates, and a run
   containing a cancelled request reports a floor, not a total.

### Status at end of entry

The four findings from the first live run are fixed and covered by tests, and a second live run
confirms all four in practice. Committed and pushed. The interface remains unvalidated by use.

---

## 2026-09-19 — Prompt [008](prompts/008-state-consistency.md), state consistency

**Instruction:** Fix three state-consistency defects before adding features or spending on further
live runs. No paid live run this iteration.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

### What was wrong

**1. A recommendation could rest on an overtaken comparison.** `permitted_actions()` offered
`recommend` whenever `session.comparison` existed, with no check that the comparison still
reflected the manager's answers. A manager who answered a question after a comparison was made
would get advice built on the analysis their answer had just superseded.

**2. Outdated results were indistinguishable from current ones.** The session view returned the
stored recommendation with nothing to say whether it was still valid. If a refresh failed, the
interface would present the superseded advice as the standing recommendation.

**3. The interface confused a pending round with an unanswered question.** `AdvisoryThread` used
`status === "unanswered"` to decide whether to show an editable field and the Send button. After
the manager submitted a round leaving one question blank, that question kept asking for input the
manager had already declined to give by omission.

Related, and fixed with them: `answers_version` advanced on every submission, so resubmitting
identical answers invalidated a perfectly current comparison and recommendation.

### What was done

**Prerequisite, enforced three times.** `recommend` is offered only when the comparison is current.
The validation boundary rejects a recommendation whose context says the comparison is stale, and
the commit boundary refuses to write one regardless of how the context was built. Recorded as
D-035. The selector prompt, now at version 1.2.0, explains that a `still_current: false` comparison
must be refreshed before recommending and that `compare` is the action for it.

**Diagnosis stays optional and the workflow stays adaptive.** The new rule mentions no order. A
test pins that a session can go compare then recommend in a single turn with no diagnosis at all.

**History kept, currency reported.** `comparison_status` and `recommendation_status` report current
or outdated. A current recommendation comes back as `recommendation`; one the answers have overtaken
comes back as `previous_recommendation`, so an interface cannot show it as standing advice by
forgetting to check a flag. A `history` list reports every accepted output with its status,
including `superseded`. Recorded as D-036.

**Submission separated from change.** `record_answers` returns whether anything actually changed and
advances `answers_version` only then, comparing answer text after trimming whitespace. Round
submission is tracked separately, by `responded_rounds`. Recorded as D-037.

**The interface uses the round, not the status.** `awaiting_response` per question drives the form
and the Send button. Unanswered questions from a submitted round stay visible as open unknowns with
a line saying nothing further is needed. The advice panel labels an outdated recommendation clearly,
dims it, and points at Continue. The comparison block does the same when it is awaiting an update.

**A turn with one possible action makes no request.** When the only permitted action is
`await_user`, the selector is not called. Spending a request to hear the only possible answer was
the remaining path by which an identical resubmission could still cost money.

### Checks performed

All deterministic. **No live run in this iteration, as instructed.**

| Check | Result |
|---|---|
| `pytest backend` | **168 passed**, 0 failed (was 150) |
| Frontend `tsc --noEmit` | Passes |
| `npm run build` | Passes |
| A genuinely new answer makes the comparison outdated | Passes |
| Recommendation refused while the comparison is outdated, in permitted actions | Passes |
| Refused at the validation boundary | Passes |
| Refused at the commit boundary, independently | Passes |
| Refreshing the comparison makes recommending available again | Passes |
| Diagnosis remains optional under the new prerequisite | Passes |
| Continue reuses a current comparison, two requests not three | Passes |
| Identical resubmission: nothing invalidated, no version bump | Passes |
| Identical resubmission: **zero provider requests** | Passes |
| Trailing whitespace is not a new answer | Passes |
| Answering a previously skipped question does count as a change | Passes |
| Failed refresh keeps history and does not present stale advice as current | Passes |
| Timed-out refresh behaves the same | Passes |
| One answer, one skip, one blank completes the round with all three statuses | Passes |
| The API view separates answer status from awaiting a reply | Passes |
| The API does not serve an outdated recommendation as current, end to end | Passes |

### Limitations

1. **Visual verification is still pending.** No browser interaction is available in this
   environment. The frontend type-checks and builds, and the state it renders is covered by tests
   at the API level, but nobody has looked at the rendered page. The outdated-advice banner, the
   dimmed shortlist and the settled-question list have not been seen.
2. **No live run.** The selector prompt changed and its effect on the model's choices is untested
   against the real service. Whether the advisor now refreshes a stale comparison when told to is a
   prompt behaviour, and only a live run can show it. The application-level guarantee does not
   depend on it: if the selector chooses wrongly, the choice is rejected.
3. **Staleness is tracked at session granularity.** Any answer change marks the whole comparison
   outdated, even one that could not affect it. That is the conservative direction and is cheap to
   refine later if it proves annoying.

### Status at end of entry

The three state-consistency defects are fixed, each covered by deterministic tests. Committed and
pushed. Stopping for visual review.

---

## 2026-09-19 — Prompt [009](prompts/009-interface-improvements.md), interface improvements

**Instruction:** Act on what the browser walkthrough showed. No new features, no paid live run.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

### What the walkthrough had shown

The first real browser session surfaced four presentation problems. The advice itself was sound;
the page around it was not.

1. The start button sat below the entire context form.
2. The busy indicator was at the top of the thread, invisible when submitting from the bottom.
3. Three fully expanded columns left the recommendation about a third of a laptop screen wide.
4. Only a status tag was shown for each answered question, never the text submitted.

### What was done

**The action before the form.** The context panel leads with the organisation, a count of what the
brief holds, and the start button. Everything else is in collapsed labelled sections. Long values
became auto-growing textareas. Recorded as D-038.

**Progress beside the control.** A spinner and label sit next to Send, the button is disabled and
relabelled while working, a live region announces the change, and a second press is ignored. The
status says only what the application knows: that a step is running and that it can take up to a
minute. Recorded as D-039.

**Hierarchy.** Summary, stances and unknowns stay visible. Assumptions, risks, the confidence note,
diagnosis findings and comparison evidence fold into labelled sections. Uncertainty never folds;
workings do. Nothing is truncated. The layout is now a sidebar plus one wide column with the advice
above the thread, and version and stage moved out of the header to diagnostics. Recorded as D-040.

**The submitted answer is shown back.** The API returns `answer` per question, null unless
answered, and the interface displays it under the question with a caveat that answered means
replied, not verified. Recorded as D-041.

### Checks performed

Backend and build checks are ordinary test runs. **The visual checks are replay-based**: a small
server in the scratchpad served the session payloads recorded during the real OpenAI run of
2026-09-18, so the interface could be driven end to end at two viewports. **No model request was
made in this iteration and nothing was spent.** These screenshots show presentation only. They are
not evidence about the advisor's behaviour, which only a live run provides.

| Check | Result |
|---|---|
| `pytest backend` | **169 passed**, 0 failed (was 168) |
| New test: the view returns the submitted answer text, null when skipped or unanswered | Passes |
| Frontend `tsc --noEmit` and `npm run build` | Both pass |
| Start button visible without scrolling, 1440 × 900 and 1366 × 768 | Yes at both, at y = 332 |
| Header content | "Ready · Credentials are checked on the first request." No version or stage |
| Auto-growing fields clipped | 16 fields, **0 clipped**, at both viewports |
| Submit row visible in the viewport while working | Yes at both |
| Button label and state while working | "Sending…", disabled; a second press was attempted and ignored |
| Focus after a recommendation arrives | Lands on `advice-heading` at both viewports |
| Advice panel width | **900px** at both, against roughly 330px before |
| Settled questions and submitted answer shown | 3 settled, 1 answer displayed with its text |
| Expandable comparison evidence opens with full content | Yes |
| Page errors, console warnings | None |

One defect was found by looking at the first pass of screenshots and fixed before the second: in
the narrow sidebar the section hint overflowed its summary and was clipped. Summaries now wrap.

### Honest note on the walkthrough being displayed

The recorded session answered a staffing-capacity question with document-volume information. That
is now visible in the interface rather than hidden behind a status tag. The volume was supplied;
staffing capacity remained unknown, and the advice still lists it as an open unknown. No staffing
answer was invented and no historical result was altered.

### What remains unverified

1. **No live run this iteration.** The interface changes have not been exercised against real
   model timing. In particular the "up to a minute" wording is drawn from the earlier measured
   runs, not from anything observed today.
2. **Nobody has used the page by hand.** These checks were driven by Playwright. Keyboard
   navigation, screen reader output and pointer interaction beyond clicking are unverified.
3. **Only two viewports.** 1440 × 900 and 1366 × 768. Narrower breakpoints exist in the stylesheet
   but were not inspected.
4. **One remaining console observation**, unchanged from the first walkthrough: a
   `GET /api/health :: net::ERR_ABORTED` in development, caused by React's double effect in strict
   mode aborting the first fetch. Harmless and development-only, but it appears in the network
   panel.

### Status at end of entry

Interface reworked, verified by replay at two viewports, committed and pushed. Screenshots are
local only and untracked. Stopping for review.

---

## 2026-09-19 — Prompt [010](prompts/010-provenance-and-final-live-run.md), provenance, wording, stance semantics and the final live run

**Instruction:** Establish where the replayed screenshots came from, correct the waiting message,
clarify what each recommendation stance means, and run one final live browser session.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

---

### Part A — provenance of the screenshot sets

The reviewer noticed that the latest screenshots differ from the earlier browser walkthrough: a
different skipped question, and a different stance for the chatbot. **They are different sessions.**
The differences are model output varying between executions, not anything the frontend did.

Established from session identifiers in the recorded payloads and from file modification times:

| Screenshot set | How produced | Session | When |
|---|---|---|---|
| `screenshots/*.png`, 17 files | **Live browser session** | **not recorded** | captured 2026-09-19 17:21 to 17:23 |
| `screenshots/ui-002/`, 20 files | **Replay** of a recorded run | `08624152de60` | recorded 2026-09-18 23:32; replayed 2026-09-19 18:21 |
| `screenshots/ui-002-review/01`, `02` | **Live application**, no model request | none created | 2026-09-19 18:43 |
| `screenshots/ui-002-review/03`, `04`, `04b` | **Replay** of the same recording | `08624152de60` | replayed 2026-09-19 18:43 |
| `screenshots/final-live/`, 9 files | **Live browser session** | `40879adc7c67` | 2026-09-19 19:08 to 19:11 |

The replay server reads `run2-01-start.json` and `run2-02-answers.json`, both carrying
`session_id: 08624152de60`.

**Reconciling the two observations the reviewer raised:**

- *Skipped question.* Session `08624152de60` asked `Q-TEAM`, `Q-BUDOK`, `Q-DATAAVAIL`, and the
  skipped one was `Q-BUDOK`, about budget approval. The browser walkthrough asked a different set
  and skipped a board-review-date question. Neither is wrong; they are different generated
  questions from different runs.
- *Chatbot stance.* `08624152de60` produced `not_recommended`. The browser walkthrough produced
  `insufficient_information`. Both are genuine model output. The inconsistency between them is what
  Part C addresses.

**What could not be established.** The browser walkthrough's session identifier is **not
recoverable**. Its payloads were never written to disk, only screenshots were taken, and sessions
are held in memory and lost on restart. Nothing has been reconstructed to fill that gap. All
existing captures and recordings are unchanged.

**One ordering point worth stating plainly**, since it is easy to read backwards: the replayed
recording is *older* than the browser walkthrough it was compared against. `08624152de60` ran on
2026-09-18 at 23:32; the walkthrough ran on 2026-09-19 at 17:21.

---

### Part B — the waiting message

"This can take up to a minute" is replaced by "The advisor is working. This may take a few minutes"
in the visible notice, the status beside the submission control and the accessible announcement.
The README's "expect roughly a minute" is corrected the same way. Recorded as D-042.

Historical worklog entries are unchanged; the earlier wording appears there as a record of what was
said at the time.

---

### Part C — stance semantics

The runtime prompts now state what each stance answers, and give a test for choosing between them.
`not_recommended` needs supplied evidence supporting a substantive reason against the option;
`insufficient_information` means the evidence does not support assessing it. The prompt is explicit
that the two are compatible with telling a manager not to start yet, and that retreating to
uncertainty when grounds exist is its own error. Recorded as D-043.

Applied in `recommend.md` 1.2.0, `compare.md` 1.2.0 and `system/advisor.md` 1.2.0. Nothing
chatbot-specific was hard-coded, no ranking imposed, nothing relabelled in the frontend, and no
extra model call added.

---

### Part D — the final live run

**This was a real execution against OpenAI through the interface.** Not a replay. The replay server
was not running; the health endpoint was checked for the absence of its marker before starting.

| | |
|---|---|
| Revision under test | `8f0c1847bd7eec4248b3eb3475b9f7ed9a1e8b32` |
| Prompt versions | system.advisor 1.2.0, action.next 1.2.0, action.clarify 1.1.0, action.diagnose 1.1.0, action.compare 1.2.0, action.recommend 1.2.0, support.repair 1.0.0 |
| Model | `gpt-5-mini`, reasoning effort `low` |
| Session | `40879adc7c67` |
| Viewport | 1366 × 768 |

**Action sequence, as it actually happened.**

Turn 1: `ask_clarification`, 21.3 seconds. Three questions, about budget confirmation, internal
staff capacity, and whether telemetry exists.

The questions were read before anything was typed. The staffing question was answered with a short
fictional reply that addresses it directly and fits the brief: about 1.5 full-time equivalents over
three months, split across the operations director, a dispatcher and the single IT analyst, with no
data engineer and no prior AI project. The budget question was skipped. The telemetry question was
left blank.

Turn 2: `diagnose`, then `compare`, then `recommend`, 101.1 seconds in total. Diagnosis ran before
the comparison, and one clarification round was used.

**Counts and usage.** Every figure below came from the provider; none is missing and none is
assumed.

| Measure | Value |
|---|---|
| Provider requests | 8 (4 selector, 4 action, 0 repair) |
| Outputs rejected by validation | 0 |
| Repairs | 0 |
| Cancelled or failed | 0 |
| Requests with no usage reported | 0 |
| Input tokens | 31,000 |
| Cached input tokens | 0 |
| Output tokens | 9,079, of which 2,048 reasoning |
| Total counted | 40,079 |
| Estimated cost | **$0.026** at published rates |
| Wall clock | 122.4 seconds of model work across two turns |

Reasoning tokens are inside the output total and are not added to it.

**What the run confirms.**

- Submitted answers stay visible. The staffing answer is rendered under its question with the
  caveat that answered means replied.
- The three statuses are distinct and correct: skipped, answered, not answered.
- Unresolved information stays explicit. `Q-BUDGET` appears in the open unknowns marked as skipped,
  and the unanswered telemetry question appears as unknown.
- The recommendation rests on a current comparison: `comparison_status` and
  `recommendation_status` both report `current`, `previous_recommendation` is absent, and the
  comparison and recommendation records both carry answers version 1, matching the session.
- The chatbot came back `insufficient_information` with a sequencing instruction rather than a
  verdict, which is the outcome Part C aimed for.

**Checks run before the live session:** 169 backend tests passing, frontend type check and
production build both passing. The revision was committed and pushed before any provider request.

### Limitations

1. **One run.** The stance change was observed once. Prompt behaviour varies between executions,
   and a single agreeing run is weak evidence. Session `08624152de60` produced the opposite label
   under the older prompts, but the comparison is not controlled.
2. **Nobody has used the interface by hand.** Every walkthrough has been driven by Playwright.
   Keyboard navigation, screen reader output and pointer behaviour remain unverified.
3. **The earlier walkthrough's session identifier is unrecoverable.** Stated as a gap rather than
   filled in.
4. **Revision is still validated but not offered**, persistence is still in memory, and offline
   fixture replay is still not implemented.
5. **No cached input tokens have ever been observed**, across all four live runs. The assembled
   input differs per call, so there may be little to cache. Nothing is concluded from that.

### Status at end of entry

Provenance documented, wording corrected, stance semantics clarified, and one final live browser
session completed and recorded. Screenshots are local and untracked. The real application is left
running.

---

## 2026-09-19 — Prompt [011](prompts/011-staffing-consistency-correction.md), staffing consistency

**Instruction:** Correct the staffing inconsistency the reviewer found in the demonstration data,
and verify it with one live session. Scope limited to that.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

---

### Part A — correction to the previous entry

**The fictional answer submitted in session `40879adc7c67` was internally inconsistent, and that
was my error in composing it.** The answer addressed the question that was asked, which was the
point of that run, but its arithmetic did not hold:

| Component | As written | In FTE, five-day week |
|---|---|---|
| Operations director | one day a week | 0.2 |
| Dispatcher | half a day a week | 0.1 |
| IT analyst | 40% of their time | 0.4 |
| **Total** | stated as "about one and a half" | **0.7** |

The headline figure and the breakdown disagree by more than a factor of two.

**The diagnosis did not detect it.** Read in full from the saved output for that session, the
diagnosis reported exactly one contradiction, and it was a different one: that the brief says the
operations director "believes" the budget is approved while no written confirmation exists. On
staffing it recorded a gap, not a contradiction, and repeated the headline number without checking
it:

> "Team constraint exists but was not quantified in the brief; however a staffing answer was
> provided indicating about 1.5 FTE available for three months and no data engineer."

The summary carried the same figure forward, "≈1.5 FTE over three months", and so did the
recommendation. The advisor took the stated total at face value and never reconciled it against the
components it was given in the same sentence.

**Nothing has been altered.** Session `40879adc7c67`, its screenshots in
`.local-review/screenshots/final-live/`, its trace and the worklog entry describing it are
unchanged. This is an appended correction, not a rewrite.

**What this says about the product.** Arithmetic consistency inside a manager's own answer is not
something the advisor currently checks, and nothing in this iteration changed that. The diagnosis
prompt asks for contradictions in the brief; it does not ask for the numbers to be reconciled. A
manager could state a total that their own breakdown does not support and the advice would be built
on the wrong figure. Worth considering as a later change, and deliberately not attempted here.

---

### Part B — the corrected demonstration

**Staffing was supplied in the brief, not as a clarification answer.** The existing `CON-TEAM`
headcount constraint, previously empty, was filled in through the interface before the session
started, so the advisor received the capacity regardless of which questions it chose to ask. It did
not ask about staffing in this run, which is consistent with having been told.

The text entered:

> "We can allocate a total of 0.7 full-time equivalents over the next three months: the operations
> director at 20% of a full-time working week, one dispatcher at 10%, and our only IT analyst at
> 40%. These allocations total 70% of one full-time role. We have no data engineer and no previous
> AI project experience. Work beyond this internal capacity would require an external contractor;
> contractor availability and funding are not confirmed."

| | |
|---|---|
| Revision under test | `16b2ee11547a1e8550ab701f0593adac5a003af0` |
| Session | `2a60d8040351` |
| Model | `gpt-5-mini`, reasoning effort `low` |
| Prompt versions | system.advisor 1.2.0, action.next 1.2.0, action.clarify 1.1.0, action.diagnose 1.1.0, action.compare 1.2.0, action.recommend 1.2.0 |
| Viewport | 1366 × 768, real application, no replay |

**Action sequence, as it actually happened.**

1. Turn 1, 16.5s: `ask_clarification`. Three questions, about written budget confirmation,
   contractor procurement, and what historical operational data exists.
2. The questions were read before anything was typed. The data question was answered with a short
   fictional reply consistent with the brief: four years of shipment timestamps at about 9,000
   deliveries a month, 14 months of GPS covering about 45 of the 60 vehicles, paper driver logs,
   around 400 scanned customs PDFs a week, all hosted in the company's own Frankfurt data centre.
   The budget question was skipped. The contractor question was left blank.
3. Turn 2, 31.3s: `diagnose`, then the selector chose `await_user` and the turn paused. **No error.**
   The interface offered Continue, which is what that state is for.
4. Turn 3, 75s, via Continue: `compare`, then `recommend`.

**The staffing figure in the advice.** Searched across the whole session payload:

| Figure | Occurrences |
|---|---|
| 0.7 FTE | **9** |
| 1.5 FTE | **0** |

It appears in the comparison's feasibility constraints, in an assumption about whether that
capacity is sufficient in skill as well as time, and in the recommendation: route optimisation
"likely [needs] more data-engineering/optimisation effort than you can safely run on 0.7 FTE
without confirmed contractor access."

**Counts and usage.** Every figure came from the provider; none is missing.

| Measure | Value |
|---|---|
| Provider requests | 9 (5 selector, 4 action, 0 repair) |
| Rejected outputs, repairs, cancelled, failed | 0, 0, 0, 0 |
| Requests with no usage reported | 0 |
| Input tokens | 35,582, of which **18,560 cached** |
| Output tokens | 11,097, of which 2,496 reasoning |
| Total counted | 46,679 |
| Estimated cost | **$0.027** |
| Model time | about 123 seconds across three turns |

**Cached input tokens were observed for the first time.** Every previous live run reported zero.
One run is not a pattern and nothing is concluded from it beyond the fact that it happened.

**State consistency.** `comparison_status` and `recommendation_status` both report `current`, there
is no superseded recommendation, and the comparison and recommendation records carry the same
answers version as the session.

The undescribed chatbot again came back `insufficient_information`, with the reasoning that without
scope, channels or conversational logs its effort and impact cannot be judged. That is the second
live run to produce that outcome under the 1.2.0 prompts.

---

### What this run does and does not show

**It shows** that a coherent staffing capacity supplied in the brief is carried correctly through
diagnosis, comparison and recommendation, with no trace of the earlier inconsistent figure.

**It does not show** improved contradiction detection. No model-behaviour change was made in this
iteration, and Part A records that the earlier contradiction went unnoticed.

### Limitations

1. **The recommendation was not captured in the interface.** The walkthrough script closed the
   browser at the pause after diagnosis, and **the interface cannot resume an existing session**:
   there is no route or control that loads a session by identifier, so a closed tab loses access to
   advice the backend still holds. The session was completed with the same request the Continue
   button issues, and its result is recorded here and in the trace, but the recommendation and
   uncertainty screenshots for this run come from the API rather than the page. Rather than start
   another paid session for prettier evidence, this is reported as a gap. The interface limitation
   is itself worth fixing later.
2. **One run.** As with every live observation in this repository.
3. **Arithmetic inside a manager's answer is still unchecked**, as Part A sets out.
4. Revision remains validated but not offered, persistence remains in memory, and offline fixture
   replay remains unimplemented.

### Status at end of entry

Demonstration data corrected and verified live. Screenshots local and untracked. The real
application is left running.

---

## 2026-09-19 — Prompt [012](prompts/012-session-recovery.md), reopening an existing session

**Instruction:** Add the smallest frontend change that reopens an existing backend session, then
capture the completed corrected example without any new model requests.

**Performed by:** Claude, via Claude Code, under the project owner's direction.

---

### The session was preserved first

Before touching anything, `GET /api/sessions/2a60d8040351` and its trace were fetched and saved to
the ignored local review directory. The backend was left running throughout, because its sessions
are in memory and a restart would have lost the one this iteration exists to photograph.

**Provider attempts at that point: 9.**

### What was added

`fetchSession()` in the frontend client, one `GET` against the endpoint the backend already had.

In the shell: a `?session=<id>` parameter is read on startup, the session is fetched, and its brief,
questions, comparison, recommendation and status are restored. On that path the sample scenario is
not requested at all, so it cannot overwrite a restored brief. A session created in the browser
writes its identifier into the URL through `replaceState`.

A 404 produces a clear notice saying the session was not found, that sessions are held in memory
and are lost when the advisor restarts, and that nothing has been started. It offers one control,
which loads the sample brief and still leaves the advisor to be started deliberately.

The example session identifier is not in the code. It is read from the URL.

Recorded as D-044.

### Verification, at 1366 × 768 against the real backend

| Check | Result |
|---|---|
| Open `?session=2a60d8040351` | Restored. Banner reads "Reopened … as the advisor left it. Nothing was regenerated." |
| Stances rendered | 3: recommended, consider later, not enough information |
| Reload the page | Still restored, 3 stances |
| Fresh browser context, same URL | Still restored, 3 stances, same summary |
| Restored staffing constraint | Contains `0.7`, does not contain `1.5` |
| Comparison and recommendation status | Both `current` |
| Missing session, bogus identifier | Clear notice, 0 stances, real session untouched |
| The offered control after a missing session | Loads the sample brief, starts nothing |
| **Every `/api` request the page made** | **All GET. Zero non-GET requests** |
| **Provider attempts before / after** | **9 / 9, unchanged** |
| Accepted records, turn number | 4 and 3, unchanged |
| Page errors | None |
| Frontend type check and production build | Both pass |

### The screenshots this produced

Saved under `.local-review/screenshots/final-coherent-restored/`. **These show the current frontend
displaying an already completed live session, fetched from the real backend. They are not a new
model execution**, and no provider request was made while taking them.

They close the gap left by the previous entry, which recorded that the recommendation for session
`2a60d8040351` could not be photographed because the interface could not reopen it. It can now.

### Limitations

1. **This is recovery, not persistence.** A backend restart loses every session. The link then
   reports the session as unavailable, which is the honest outcome, but the advice is gone.
2. **No sharing.** The URL works only against a backend that still holds that session in the same
   process. It is not a shareable record of the advice, and export remains unimplemented.
3. **No listing.** There is no way to see which sessions the backend holds, so a lost identifier
   is a lost session even while the process is running.
4. **One run's worth of evidence**, as with everything live in this repository.

### Status at end of entry

Session recovery implemented and verified without spending anything. Screenshots and saved
responses are local and untracked. The real backend is left running, still holding session
`2a60d8040351`.
