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
