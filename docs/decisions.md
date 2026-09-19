# Decision record

Each entry states the decision, why it was taken, and what was rejected. Superseded decisions are
kept with their replacement named, because the assessment is partly about how the design evolved.
Entries are not deleted.

**Status values:** Confirmed by the project owner. Proposed and awaiting review. Superseded. Open.

---

## D-001 — Implement the IoC method, not the BlueCallom platform

**Status:** Confirmed · 2026-09-18

We implement the principles stated on
<https://bluecallom.com/intelligence-over-code-method/> in our own stack. We do not imitate
GPTBlue Studio or borrow its component vocabulary.

**Why:** We have no access to the platform. Claiming to have used its internals would be a
fabrication, and an assessor from BlueCallom would see it immediately. A faithful implementation
of the stated principles is both honest and more defensible.

---

## D-002 — Runtime prompts as version-controlled files loaded at runtime

**Status:** Confirmed · 2026-09-18

Runtime prompts live in `backend/prompts/` as Markdown with front matter declaring identifier,
version, role, inputs, outputs and constraints. Python loads them from disk. No prompt text in a
Python string literal.

**Why:** The source page claims better models yield better responses "without needing to change a
single line of code." That claim is untestable if prompts are literals inside application logic.
Files on disk also make the prompts reviewable as the primary artefact, which is what the method
asserts they are, and put their evolution in Git history.

**Rejected:** Prompts in a Python module, which defeats the purpose. Prompts in a database, which
adds a dependency and hides how the intelligence evolved.

---

## D-003 — Comparison is qualitative and provenance-labelled. No weighted scoring in the MVP

**Status:** Confirmed · 2026-09-18 · **supersedes D-003a**

Each initiative is compared through five separately labelled categories: stated facts,
assumptions, missing evidence, feasibility constraints, and trade-offs. No numeric score, no
weights, no ranking arithmetic in the MVP.

**Why:** Directed by the project owner, and correct on the merits. A weighted score over partial
information manufactures false precision. Its specific failure is that an unknown has to become
some number, and whatever number is chosen, the option we know least about is silently penalised
or silently flattered. A manager cannot audit that, because the arithmetic hides the provenance
of every input.

The five-category structure keeps provenance visible instead: a recommendation resting on an
assumption has to say so, in its own field. That is a structural guarantee about where a claim is
written down, not a guarantee that it was categorised honestly or that it is true. See D-016.

**Rejected:** Weighted scoring in the MVP. If it returns later, it arrives with documented scales,
documented weights and a written statement of its limitations, never implicitly.

### D-003a — Superseded: "the model judges, Python counts"

**Status:** Superseded on 2026-09-18 by D-003.

The earlier design had the model assign per-criterion scores and weights, with Python computing
weighted totals, ranks and revision deltas. It was withdrawn at the project owner's direction
before any implementation. Recorded here because the reasoning behind its withdrawal is part of
the design argument, not because any code was written against it.

---

## D-004 — A bounded advisory loop, not a fixed pipeline

**Status:** Confirmed · 2026-09-18 · **supersedes D-004a**

Diagnosis, clarification, comparison, recommendation and revision are advisory responsibilities,
each with its own prompt and its own place in the interface. A prompt chooses which action is
appropriate given the session state. Code fixes the set of permitted actions and the limits on the
loop.

**Why:** The source page uses orchestration language without prescribing a sequence. Under the
method's hierarchy, deciding what to do next given a manager's situation is a judgement, and
judgements belong in prompts. A fixed order in Python would put the central process decision in
the subordinate, and would also produce bad advice: a well-specified brief does not need
clarification, and a vague one may need it more than once.

**Rejected:** A fixed five-step sequence. Also rejected: a single mega-prompt, which would be
cheaper and would make both the method and the revision delta invisible.

### D-004a — Superseded: the fixed five-stage pipeline

**Status:** Superseded on 2026-09-18 by D-004.

The original design ran diagnose, clarify, compare, recommend and revise in a fixed order, one
endpoint each. Corrected at the project owner's direction before implementation. No code was
written against it.

---

## D-005 — Code enforces schemas, limits, state integrity and action contracts

**Status:** Confirmed · 2026-09-18

Four controls sit in Python and cannot be waived by any prompt: schema validation of every model
response, execution limits on the advisory loop, append-only validated state transitions, and a
fixed contract of permitted actions.

**Why:** Directed by the project owner, and necessary. We verified that the BlueCallom source page
says nothing about validation, schemas, limits or control, so these are our engineering judgement
and the documentation says so rather than attributing them to the method.

They are compatible with the hierarchy because they decide nothing. No guard has an opinion about
which initiative is better. They are the "precision" case that the page reserves for code when it
states that IoC "has nothing to do with 'No-Code'."

**Rejected:** Pushing these controls into prompt text to reduce the Python line count. That would
be method theatre and would produce an application that cannot be trusted to terminate.

---

## D-006 — React with Vite and TypeScript

**Status:** Confirmed · 2026-09-18 · **amends D-006a**

**Why, on suitability:** Several coordinated panels over one evolving session object, updated
partially per advisory turn, is React's core competence.

**Why, on maintainability:** TypeScript makes the API contract explicit at the boundary most
likely to break silently. Every backend response is already a declared Pydantic contract;
mirroring it in TypeScript catches drift at compile time rather than during a demonstration.
Vite needs no build configuration and proxies the API, removing CORS from the developer's
concerns.

**On component libraries:** We start with plain CSS modules and design tokens because assessment
part 3 asks us to explain the UI/UX decisions, and a hand-built layout makes those decisions ours
to explain. This is a choice about the deliverable, not a methodological objection. Adopting a
headless library later for accessible dialogs, comboboxes or focus management would be an
improvement.

### D-006a — Corrected claim

The previous revision implied that TypeScript and component libraries sit awkwardly with
Intelligence-over-Code. That was wrong and the project owner corrected it. The method's hierarchy
concerns where business judgement lives, not the typing discipline or UI toolkit of the
presentation layer. Neither a type annotation nor a button component holds an opinion about which
initiative to fund.

---

## D-007 — Python with FastAPI

**Status:** Confirmed · 2026-09-18

**Why, on suitability:** Pydantic. Validating model output against a declared contract is the most
important code in an application of this kind, and FastAPI makes it the default path. The Python
SDK ecosystem for model providers is the most mature.

**Why, on maintainability:** Generated OpenAPI documentation describes the HTTP surface without a
separate document that drifts. Guards and validation are pure functions, unit testable with no
model and no network.

**Alternative considered:** A single Next.js application with API routes, which would remove a
process and a port. We preferred the split for Pydantic's declarative validation and for the
project owner's familiarity with Python at that layer. See D-018 for the corrected reasoning; the
earlier claim that this choice was about protecting the method has been withdrawn.

---

## D-008 — One startup command via a root npm script

**Status:** Confirmed · 2026-09-18

After first-time setup, `npm run dev` from the repository root starts both processes through
`concurrently`.

**Why:** The brief asks for a simple documented startup command. The development machine is
Windows, where a Makefile would need extra tooling. A root npm script is cross-platform and costs
one dev dependency.

**Rejected:** A Makefile. Also rejected: parallel shell and PowerShell scripts that would need to
be kept in step.

---

## D-009 — Offline fixture mode, labelled, and never a fallback

**Status:** Confirmed · 2026-09-18

The model client can replay recorded fixtures instead of calling a provider. Two rules: the
interface labels fixture output as sample data, and a failed live call never silently becomes a
fixture response. Offline mode is entered by configuration, deliberately.

**Why:** A reviewer may have no API key, no budget or no network, and an application that cannot
be run cannot be assessed. The two rules exist because a demonstration that quietly substitutes
canned answers for a failed call is misleading about what the software actually does, which is a
worse failure than an error message.

**Rejected:** Requiring a live key. Also rejected, and never acceptable: shipping a key.

---

## D-010 — Fictional demonstration data only

**Status:** Confirmed · 2026-09-18

Fictional organisations, initiatives and budgets, labelled as sample data in the interface.

**Why:** Directed by the project owner, and correct regardless. Real employer data in a repository
intended for public review would be a confidentiality breach. Inventing plausible BlueCallom
customer data would be worse.

---

## D-011 — Development prompts and runtime prompts are separate artefacts

**Status:** Confirmed · 2026-09-18

`docs/prompts/` records the instructions that produced the software, verbatim and in order.
`backend/prompts/` holds the prompts the software executes.

**Why:** The assessment asks separately for a working application and for an account of how it was
built. Merging the two would obscure which prompts a user of the application is actually subject
to.

---

## D-012 — This application covers assessment parts 2 and 3 only

**Status:** Confirmed · 2026-09-18

The repository addresses building the application and designing its interface. The candidate's
prior professional work is presented separately by the project owner.

**Why:** Directed by the project owner. This application was built for the assessment, starting
2026-09-18, and its Git history says so. Presenting newly written code as evidence of earlier
professional experience would misrepresent the candidate's record, which is a far more serious
problem than any technical shortcoming in the code.

---

## D-013 — Record AI assistance accurately

**Status:** Confirmed · 2026-09-18

The repository states that ChatGPT supported requirements analysis and development-prompt
preparation, and that Claude performs implementation under the project owner's direction. No
document implies that every line was typed by hand.

**Why:** Directed by the project owner, and it is the honest description of how this repository is
produced. In an assessment about AI-assisted development, misrepresenting the process would
undermine the submission more than the assistance ever could.

---

## D-014 — Runtime model provider deliberately left open

**Status:** Open · 2026-09-18

The provider choice is deferred until available API access is confirmed. The model client is
defined as an interface with adapters behind it.

**Why:** Directed by the project owner. The decision affects one module. Deferring it blocks
nothing in the skeleton, the guards, the schemas or the interface, and committing early to a
provider we may not have credentials for would be the more expensive mistake.

---

## D-015 — Local addresses are fixed, not configurable

**Status:** Confirmed · 2026-09-18

The backend binds `127.0.0.1:8000` in `scripts/dev-backend.mjs`. The dev server serves port 5173
and proxies to that address, set in `frontend/vite.config.ts`. `BACKEND_HOST` and `BACKEND_PORT`
are removed from `.env.example` and from the settings object.

**Why:** Those variables were advertised but never read. Nothing passed them to Uvicorn, so
setting them would have changed nothing while appearing to change something. That is worse than
no option at all, because it fails silently. For a local-only MVP, two fixed addresses in two
named files are simpler than a configuration path nobody uses.

**Rejected:** Wiring the variables through to the startup script. It would have made the
documentation true, but it adds a configuration surface the project does not need yet. If
deployment ever comes into scope this decision should be revisited, and at that point the values
should be read in one place rather than two.

---

## D-016 — What schema validation and reference checks actually establish

**Status:** Confirmed · 2026-09-18 · **corrects an overclaim**

Structural validation and referential checks are traceability mechanisms. They are not correctness
mechanisms, and no document in this repository may describe them as though they were.

**What they do establish.** That a payload has the declared shape. That a claim was filed under
exactly one of the five categories. That an identifier a claim points at exists in the brief or in
a clarification answer. That an action named by a prompt is one the application permits. That the
count of clarification questions in a batch is within its limit.

**What they do not establish.** That a statement filed under stated facts is true. That something
filed as a fact is not actually an assumption. That a cited input supports the claim citing it.
That the comparison is complete, balanced or relevant.

**Why the distinction matters here.** An earlier revision of the architecture said that separate
schema fields mean "an assumption cannot arrive labelled as a fact." That is false. A model can
put anything in any field, and the schema will accept it as long as the shape is right. The honest
claim is narrower and still worth having: **traceability makes a wrong claim findable, cheaply and
by a reader who is not the author.** It does not prevent one.

**Consequence for the code.** Validators check structure and referential integrity only. They
contain no rule about what makes a good initiative, no keyword heuristics, and no attempt to judge
whether a claim belongs where it was put. Semantic quality is the prompts' responsibility and the
reviewing manager's, not the schema's.

---

## D-017 — `diagnose` is a permitted action, and every action declares its output contract

**Status:** Confirmed · 2026-09-18

The permitted action set gains `diagnose`. Each action is bound to the contract its output must
satisfy, declared once in `backend/app/models/actions.py` as `ACTION_OUTPUT_CONTRACTS` and
documented in [architecture.md](architecture.md), section 2.

**Why:** The two lists had drifted. The architecture described a `diagnose.md` prompt while the
permitted actions were `request_context`, `ask_clarification`, `compare`, `recommend`, `revise`
and `await_user`. Since a prompt can only run when the next-action step names it, the diagnosis
prompt was unreachable. Diagnosis is one of the five advisory responsibilities the brief asks for
and it appears in the interface, so the action set was wrong, not the prompt list.

Binding actions to output contracts in one place is the fix for the underlying problem rather than
the symptom. A new action cannot be added without declaring what its output must look like, and
the pairing is checked by a test.

**Note:** `await_user` has no prompt. It ends the turn and returns control, so there is no model
output to validate. It is mapped to a contract carrying only a reason, to keep the mapping total.

---

## D-018 — Stack chosen on suitability and familiarity, not on methodological necessity

**Status:** Confirmed · 2026-09-18 · **corrects D-007 and an overclaim in the architecture**

Python with FastAPI for the backend, React with Vite and TypeScript for the interface, as two
processes.

**Why, honestly stated.** Pydantic gives the strongest declarative validation of the options we
considered, and parsing model output is the code this application depends on most. The project
owner is more productive in Python at that layer. Keeping the backend separate puts the runtime
prompt files next to the code that loads them, which suits how we intend to review them. React
suits an interface of several coordinated panels over one evolving object.

**What we withdraw.** Earlier revisions said that a single Next.js application would "blur the
boundary between interface and intelligence," and that TypeScript's validation story made it
unsuitable for this method. Both claims are withdrawn. Where business judgement lives is a
question of how an application is organised, not of which language or framework carries the
transport layer. The same prompt-first separation is achievable in a single TypeScript project,
and a team more fluent in that stack should build it there.

This is the third correction in the same family, after D-006a. The pattern is worth naming: it is
tempting to dress a preference up as a methodological requirement, because that sounds more
rigorous than saying we are faster in Python. It is not more rigorous. It is just less true.

---

## D-019 — OpenAI, the Responses API, and a separate wire schema layer

**Status:** Confirmed · 2026-09-18 · closes D-014

Provider: OpenAI, via the official asynchronous Python SDK, the Responses API and native
Structured Outputs. Default model `gpt-5-mini`, configurable through `MODEL_NAME` and never
switched by the application itself.

**The compatibility problem, and what we did about it.** Structured Outputs accepts a restricted
subset of JSON Schema. It does not support `minLength`, `maxLength`, `pattern`, `minItems`,
`maxItems` or `default`, and in strict mode every property must be required. We checked our
contracts against the SDK's own strict-schema converter and **every one of them emitted at least
one unsupported keyword**: pattern-constrained identifiers, minimum text lengths, the
three-question cap, and defaults throughout.

So there are two layers. `app/models/wire.py` holds API-facing schemas that are compatible by
construction, and the application contracts stay exactly as strict as they were. Output crosses
from one to the other in the validation boundary.

**Why not relax the contracts to match.** Because the constraints are the point. A cap the API
cannot enforce is still a cap we enforce; dropping it to fit the transport would be letting the
protocol decide the product's rules. A test asserts that a four-question batch is valid on the
wire and rejected by the application, which is the behaviour we want and evidence the split works.

**Rejected:** Sending the strict contracts and hoping unsupported keywords are ignored. They are
documented as unsupported, and relying on undocumented leniency is how a project acquires a
failure nobody can reproduce.

---

## D-020 — Every provider failure is named, and none is ever papered over

**Status:** Confirmed · 2026-09-18

Missing credentials, authentication, rate limits, timeouts, connection loss, rejected requests,
refusals and truncated output each map to a distinct exception carrying whether a retry could
help. The SDK's own retry loop is disabled, so the application issues no request it did not count.

**Why:** A generic "something went wrong" tells a manager nothing and tells a developer less. More
importantly, this is where the temptation to substitute sample output lives, and the rule from
D-009 holds without exception: **a failed live call is never replaced by fixture content.** A
truncated response is discarded rather than partially used, because a comparison missing its last
initiative would validate perfectly well as a comparison.

**Rejected:** SDK-level retries. A retry the application cannot see is a request it cannot budget
for, which would make the request ceiling a fiction.

---

## D-021 — One validation boundary, and what it now catches

**Status:** Confirmed · 2026-09-18 · extends D-005

Every advisory output passes through `validate_output` before it can reach session state. There is
one entry point, because a second path would be a hole in the only wall between unchecked model
output and the manager's advice.

Two gaps found in review are now closed:

- **An unrelated context identifier used to pass.** Output naming another session's context would
  attach to whichever session received it, which is how advice about one situation gets presented
  as advice about another.
- **A revision could report a change to a constraint that does not exist.** Revision validation now
  requires two real snapshots and checks every reported before-and-after value against them.

Both have regression tests. `revise` remains unavailable in the interface: its validation exists,
its user flow does not, and advertising an action the application cannot complete would invite the
selector to choose it and then fail.

---

## D-022 — Manager text is case material, and the defences that actually hold

**Status:** Confirmed · 2026-09-18

Everything the manager typed reaches the model inside a fenced block that states it is information
rather than instruction, and the standing prompt repeats the rule. A manager who types the closing
delimiter cannot end the block early, which is tested.

**What we do not claim.** Prompt-level defences are mitigation, not proof. A determined injection
can still try, and a sufficiently clever one may succeed at influencing the text the model
produces.

**What actually holds** is structural and sits outside the model's reach. The action set is fixed
in code. Every output is validated. Every reference must resolve against the real brief. The
manager's answers are written by a path no model output touches. The request budget is counted in
Python. Text that talks its way past the prompt still cannot invent an initiative, cite a question
the manager skipped, alter an answer, or buy itself another request.

That is the honest division: the prompt discourages, the code prevents.

---

## D-023 — Sessions in memory, and a round is a unit of response

**Status:** Confirmed · 2026-09-18

Sessions live in process memory and are lost on restart. Stated in the README, in the module, and
in the diagnostics endpoint, so it is visible wherever someone might assume otherwise.

**A design correction found by a test.** The first implementation treated any unanswered question
as blocking, which deadlocked the session: a manager who answered two of three questions and left
the third alone never got advice, because the loop waited forever for a reply that was not coming.
Blocking is now per round rather than per question. Once the manager submits anything for a round,
that round stops blocking and whatever they left untouched becomes an open unknown, visible in the
interface and carried into the advice.

This is the correct semantics as well as the working one. A manager who leaves a field blank has
answered: they have said they do not want to answer it.

---

## D-024 — Configuration status means presence, never authentication

**Status:** Confirmed · 2026-09-18 · corrects a defect in D-019's implementation

One check, in `app/core/configuration.py`, used by both the health endpoint and client
construction. It rejects empty values, an explicit list of placeholders including the one committed
in `.env.example`, and providers with no adapter. It imposes **no format rule on the key itself**.

**Why the placeholder matters most.** The previous check accepted any non-empty provider and key,
so copying `.env.example` and forgetting to edit it reported the advisor as ready. That is the most
likely setup mistake there is, and the status indicator actively concealed it.

**Why no format rule.** Provider key formats change. A check that rejects a valid key is worse than
one that lets an invalid key through to the provider, where it fails with a clear authentication
error. The check catches only values no real key could be.

**Why the naming is deliberate.** The field is `model_configured_locally`, not `connected` or
`authenticated`, and every response carries a note saying what it does not cover. A manager who
sees "connected" and then hits an authentication error on their first session has been misled by
the status indicator, which is worse than having none.

**One check, not two.** A health endpoint saying the application is configured and a session
refusing to start cannot both be true, because they call the same function.

---

## D-025 — The turn budget is a deadline, not a check between steps

**Status:** Confirmed · 2026-09-18 · corrects a defect in D-005's implementation

The remaining wall-clock budget bounds each awaited call through `asyncio.wait_for`, and is
re-checked after the call returns, before anything is committed.

**The defect.** Elapsed time was tested only between loop iterations. A single slow request could
run for minutes past a 180-second limit and still commit its output, so the limit described the
loop rather than bounding it.

**Two checks, on purpose.** The timeout cancels an overdue request rather than leaving it running.
The re-check afterwards stops a result that arrived late from being written. Without the second, a
call that finished just past the deadline would still land.

A cancelled or late request is recorded as an attempt and nothing is committed. The session status
returns to ready and the lock is released through `finally`, so an overrun leaves a usable session
rather than a wedged one.

---

## D-026 — Attempts are recorded separately from accepted outputs

**Status:** Confirmed · 2026-09-18

`session.attempts` holds every provider request: selector calls, actions, repairs, rejections,
failures and cancellations, each with its prompt hash, outcome and usage. Append-only, and written
as each attempt completes so the successful ones survive a later failure in the same turn.

**Why separate.** An accepted output says what the advisor concluded. An attempt says what was
requested and what became of it. Keeping only the first lost every selector call, lost the cost of
a repair, and lost every request that failed, which is exactly what someone debugging a live run
needs to see.

**Usage is never invented.** `usage_available` is explicit rather than inferred from an empty
field. A failed or cancelled request has no usage to report, and plausible-looking token counts
would corrupt the only record of what a run actually cost. The one nuance: a call that completed
but arrived past the deadline does have real usage, and it is recorded with a note saying the
result was discarded.

Clarification records also now carry their prompt trace and usage. They previously carried neither,
which made the action a manager interacts with most the one with no record of what produced it.

---

## D-027 — One lock, covering answers and advisory execution together

**Status:** Confirmed · 2026-09-18

`run_turn` takes an optional `prepare` callable, executed inside the session lock before the turn
begins. Recording the manager's answers goes through it.

**The defect.** The answers endpoint wrote answers outside the lock, so a submission could land
while another turn was awaiting a model response. The advice would then have been generated against
one set of answers and committed against another, with nothing to detect it.

**Why a hook rather than a second lock.** There is exactly one lock in the system and nothing
inside it acquires another, so there is no acquisition order to get wrong and no deadlock to have.
A separate answers lock would have introduced both.

A failure in `prepare`, such as an answer for a question never asked, propagates to the caller with
no turn consumed and the lock released.

---

## D-028 — What we claim about schema support, and what we do not

**Status:** Confirmed · 2026-09-18 · corrects an overclaim in D-019

The wire layer stays. Its justification changes.

**What was claimed and was too broad.** That Structured Outputs does not support `pattern`,
`minLength`, `maxLength`, `minItems`, `maxItems` or numeric bounds, full stop. The project owner
reports that the documentation distinguishes additional restrictions applying to fine-tuned models,
which makes a universal claim wrong.

**What we could actually verify.** Not much, and the honest thing is to say so. The official guide
was retrieved three times and truncated before its supported-schemas section each time, so the
per-keyword list could not be read directly.

**What we claim now.** Only what we chose. The wire models use a deliberately conservative subset:
every field required, no defaults, no constraints, no numeric types. That is narrow enough that the
question of which keywords are supported does not arise for us.

**Three things kept apart.** Our chosen subset is a decision. Local schema conversion checks run
offline and prove only that our models stay inside that subset. Service acceptance is established
only by OpenAI accepting a real request, and **that has not happened yet.** No test result and no
local check is evidence of it.

The general lesson is the same one as D-016 and D-018: state the narrow true thing rather than the
broad convenient one. A local check that passes is not a remote service that agreed.

---

## D-029 — A limit reports what survived it

**Status:** Confirmed · 2026-09-18 · corrects a defect found in the first live run

When a turn stops at a limit, the message names the steps that completed and were saved, the step
that was interrupted, and what the session still holds. The interrupted step's output is discarded.
Nothing validated before it is touched.

**Why.** The previous message said "Nothing partial was saved" regardless of what had happened. In
the first live run that was simply false: a comparison had been committed and kept, and the manager
was told the opposite. A recovery message that misdescribes the state is worse than no message,
because it tells someone to redo work that already exists.

---

## D-030 — Continue resumes; it does not restart

**Status:** Confirmed · 2026-09-18

A comparison records the answers version it was made against. While it is still current, the
advisor is not offered `compare` again. Once the manager supplies more, it becomes stale and
re-comparing is available.

**Why.** After a timeout, Continue is the recovery path, and the recovery must not repeat the
expensive step that already succeeded. The rule is about staleness rather than existence, because
re-comparing genuinely is the right move once the manager has said something new.

---

## D-031 — The turn deadline is 300 seconds of headroom, not a speed-up

**Status:** Confirmed · 2026-09-18 · configurable through `MAX_TURN_SECONDS`

**This changes nothing about how long anything takes.** The requests are exactly as slow as they
were. What changed is that a turn doing comparison and recommendation now has room to finish inside
one turn instead of being cut off partway.

The first live run measured single steps between 20 and 60 seconds and a full turn exceeding 180.
The old ceiling was not a performance target being missed; it was a ceiling set before anyone had
measured the work.

---

## D-032 — A skipped question is described, never cited

**Status:** Confirmed · 2026-09-18 · the prohibition from D-021 stands unchanged

The rule does not move: a skipped or unanswered question produced no information and may not be
cited as a `clarification.answer`. What changed is what the model is told.

- The prompts carry two short worked examples: an answered question supporting a claim through
  `sources`, and a skipped one appearing as text in `missing_evidence`.
- The input now contains **two separate lists**: the answers that may be cited, with their text, and
  the status of every question asked, marked as awareness only.

**Why the split matters.** In the first live run the model received one mixed list and cited five
skipped identifiers as sources. Two action outputs were rejected and repaired, at roughly a quarter
of the session's tokens. The model was not being careless: tracing an unknown back to the question
that would have answered it is a reasonable instinct. It was being asked to filter a list when it
could simply have been given the filtered one.

In the second run, with the split and the examples, **no output was rejected.**

**What did not change.** No invented answers, and an unknown still never becomes a negative
assessment of an option.

---

## D-033 — Diagnosis is optional, and only before the comparison

**Status:** Confirmed · 2026-09-18

`diagnose` is offered while no comparison exists, and not after. It is never required.

**Why.** In the first live run the advisor compared, then diagnosed. A diagnosis is a reading of
the brief meant to aim the analysis; arriving afterwards it informs nothing. Removing it from the
permitted set once a comparison exists fixes the ordering without imposing a fixed sequence, which
the method's central claim rules out. A brief clear enough to work with can still skip it entirely,
and the second run shows the selector choosing it first of its own accord.

Clarification is also limited to one round by default. The first run asked six questions across two
rounds before comparing anything, which is more interrogation than a manager will sit through. The
advisor now proceeds after one round and records the rest as open unknowns.

---

## D-034 — Measure reasoning and cached tokens, and do not double count

**Status:** Confirmed · 2026-09-18

Each call records `reasoning_tokens` and `cached_input_tokens` when the provider reports them, and
leaves them null when it does not. Reasoning effort defaults to `low`, configurable through
`MODEL_REASONING_EFFORT`, with an empty value omitting the parameter for a model that rejects it.

**The accounting.** Reasoning tokens are already inside `output_tokens`, and cached input tokens are
already inside `input_tokens`. Both are recorded as visible subsets, never added to a total. The
reasoning guide is explicit that reasoning is billed as output; adding it would count the same
tokens twice and inflate every cost estimate in this repository.

**On cost figures generally.** Every cost in the worklog is an estimate computed from the usage the
provider returned, at published rates. A request that failed or was cancelled returns no usage. It
was still issued and may still have been billed, so a run containing one has a floor, not a total.

---

## D-035 — A recommendation requires a comparison that reflects the current answers

**Status:** Confirmed · 2026-09-19

`recommend` is offered only when a comparison exists **and** that comparison was made against the
answers the session now holds. The rule is enforced three times over: in the permitted action set,
in the validation boundary, and again at the commit boundary.

**The defect.** `recommend` was available whenever `session.comparison` existed. A manager could
answer a question, making the comparison out of date, and the advisor would build advice on the
superseded analysis. The result would contradict the answer the manager had just given, with
nothing in the output to show it.

**Why three checks rather than one.** The permitted set stops the selector choosing it. Validation
stops an output being accepted if the context is built anywhere else. The commit guard stops it
being written even if a future caller assembles the context wrongly. Each is cheap, and the
failure they prevent is advice that quietly contradicts the manager.

**This is a data-consistency prerequisite, not a sequence.** Nothing here requires diagnosis,
requires clarification, or fixes an order. It says only that advice may not rest on analysis the
manager's answers have overtaken. A brief that needs no questions still goes compare then
recommend in one turn, and a test pins that diagnosis remains optional.

A recommendation that is already current is also not offered again, so nothing is recomputed when
nothing has changed.

---

## D-036 — History is kept; currency is reported separately

**Status:** Confirmed · 2026-09-19

Every validated output stays in the session. Nothing is deleted when it goes stale. What changes
is how it is described.

- `comparison_status` and `recommendation_status` report `current` or `outdated`.
- The API returns a **current** recommendation as `recommendation`. One the answers have overtaken
  comes back as `previous_recommendation` instead.
- `history` lists every accepted output with its status, including `superseded` for earlier
  versions of the same step.

**Why the API splits the field rather than adding a flag.** A flag can be ignored. If outdated
advice arrived in the same field as current advice, any interface that forgot to check the flag
would present stale advice as standing advice, which is the exact failure being prevented. Making
the shape different means the mistake cannot be made by omission.

**When a refresh fails or times out**, the previous recommendation is not shown as current. It is
kept, labelled out of date, and the manager can continue from there. Losing it would be worse than
labelling it: it is still the last thing the advisor actually concluded.

---

## D-037 — A pending round is not the same as an unanswered question

**Status:** Confirmed · 2026-09-19

Two things are tracked separately in the session:

- **Submission.** Whether the manager has sent a clarification round. `round_is_pending()`.
- **Answer status.** What became of each question: answered, skipped or unanswered.

`answers_version` advances only when an answer's text or status actually changes. Resubmitting the
same answers marks the round submitted and changes nothing else, so no result becomes stale and no
recomputation follows. Whitespace around an answer is trimmed before comparing, so a trailing space
is not new information.

**The interface defect this fixes.** The advisory thread used `status === "unanswered"` to decide
whether to show an editable field and a Send button. After the manager submitted a round having
left one question blank, that question still looked like an outstanding request. It was not: the
manager had already decided, by omission. The thread now uses `awaiting_response`, which is a
property of the round. Unanswered questions from a submitted round remain visible as open unknowns,
with a line saying nothing further is needed.

The three statuses remain distinct throughout. Skipped is a decision the manager made, unanswered
is one they did not make, and neither is an answer.

**One consequence worth naming.** A turn where the only permitted action is `await_user` now makes
no provider request at all. Asking the selector to choose from a set of one would spend a request
to hear the only possible answer, which is precisely the recomputation an identical resubmission
must not trigger.

---

## D-038 — The action comes before the form

**Status:** Confirmed · 2026-09-19

The context panel leads with the organisation, a one-line count of what the brief contains, and
the start button. Objectives, constraints and initiatives sit below in labelled, collapsed
sections that state their own contents.

**Why.** The browser walkthrough showed the start button below every field of a brief the manager
had not asked to edit. Starting the sample scenario meant scrolling past a form to reach the one
control that mattered. Editing is the rare case; starting is the common one, and the layout had
them the wrong way round.

Nothing is removed. Every field is still editable, one click away, and the sections say how many
entries they hold so a collapsed section is not a mystery.

**Related:** long values are now auto-growing textareas. Objectives, constraint values and
initiative descriptions were clipped in single-line inputs, so a manager could not read the text
they were about to send. A check at two viewports confirms sixteen such fields with none clipped.

---

## D-039 — Progress is shown where the manager is looking

**Status:** Confirmed · 2026-09-19

Submitting a round now shows a spinner and a label beside the Send button, the button is disabled
and relabelled, and a visually hidden live region announces the change. A second press does
nothing.

**Why.** The busy indicator sat at the top of the thread. Submitting from the bottom of a question
list meant no visible feedback at all, so the only signal was a greyed-out button. On a laptop
screen that is indistinguishable from nothing happening, which invites a second press.

**What the status says, and does not.** It says a step is running and that it can take up to a
minute. There is no percentage and no intermediate stage, because the application does not know
either. Inventing them would be a progress bar that lies.

**Focus.** A new round of questions takes focus, and an arriving recommendation moves focus to the
advice heading. A jump control is also offered, since focus movement alone is easy to miss.

---

## D-040 — Scannable advice, foldable workings, visible uncertainty

**Status:** Confirmed · 2026-09-19

The advice panel shows the summary, every initiative's stance with its reasoning, and what is
still unknown. Assumptions, risks, the confidence note, diagnosis findings and comparison evidence
are in labelled expandable sections.

**The rule that governs what folds.** Uncertainty never folds. Workings do. Hiding what is not
known would turn a product built to surface gaps into one that conceals them, so both "Still
unknown" and the advisor's own open unknowns stay open while assumptions and evidence fold away.

**Nothing is truncated.** No text is cut with an ellipsis and no source is dropped. A collapsed
section states its count, and opening it shows the whole thing.

**Layout.** A fixed context sidebar and one wide column holding the advice above the working
detail. Three fully expanded columns gave the recommendation roughly a third of a laptop screen,
which is not enough width to read a paragraph, and padded the short panels out beside the long one.
Measured after the change: the advice panel renders at 900px at both 1440 and 1366 wide, against
roughly 330px before.

**Header.** Version and build stage are gone from the manager-facing header. They told a manager
nothing and occupied the most prominent corner of the page. Both remain at `/api/diagnostics`.
Configuration problems and operational errors stay visible, because those are the failures a
manager can act on.

---

## D-041 — Show the manager what they actually submitted

**Status:** Confirmed · 2026-09-19

After a round closes, each answered question displays the text the manager sent, beside its status.
The API returns it as `answer`, null for anything not answered.

**Why it matters more than it looks.** In the browser walkthrough a staffing-capacity question was
answered with document-volume information. The advisor then used the volume, and the staffing gap
stayed open. With only a status tag visible, the session looked like the question had been dealt
with. With the text visible, the mismatch is obvious to the person best placed to notice it.

**Status is not verification.** The interface says so directly: answered means a reply was
submitted, not that the reply addressed the question, was checked, or closed the gap. The same
caveat is in the API field's own documentation, so a future consumer reads it too.

That walkthrough is recorded as it happened. The volume was supplied; staffing capacity remained
unknown. No staffing answer has been invented and no historical result altered.

---

## Decisions still open

D-014 provider, plus session persistence, export formats, test depth and streaming. Tabulated with
recommendations in [requirements.md](requirements.md), section D-b.
