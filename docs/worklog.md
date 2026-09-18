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
