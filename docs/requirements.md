# Requirements

Status: **design agreed in outline, skeleton implemented, application logic not started.**
Revised following the design review in [prompts/002-design-review-and-skeleton.md](prompts/002-design-review-and-skeleton.md).

This file separates three different kinds of statement, because conflating them is the easiest
way to fail an assessment of this type:

- **A — What the assessment asks for.** Taken from the assignment as relayed by the project owner.
- **B — What BlueCallom states about Intelligence-over-Code.** Quoted from BlueCallom's own page,
  with the source named. These are constraints on *how* we build, not our inventions.
- **C — Our interpretation and implementation choices.** Everything else. These are ours to
  defend, and ours to change.

---

## A. Assessment scope

The assessment has three parts. **This application addresses parts 2 and 3 only.**

| # | Part | Addressed by |
|---|---|---|
| 1 | Describe the candidate's existing professional projects | **Not this repository.** Handled separately by the project owner |
| 2 | Build a strategy-consulting application for managers using the IoC method | This repository |
| 3 | Design a sample enterprise AI interface and explain the UI/UX decisions | This repository, through the same application |

This point is load-bearing. **This application is newly built for the assessment and is not
evidence of prior professional work.** No document in this repository may present it as such. Its
Git history begins on 2026-09-18 and shows exactly that.

### A2 expanded — what the application must do

Agreed in [prompts/001-project-brief.md](prompts/001-project-brief.md) and refined in
[prompts/002-design-review-and-skeleton.md](prompts/002-design-review-and-skeleton.md): the
application helps a manager prioritise candidate enterprise AI initiatives against their
objectives, resources and constraints. It must:

1. Ask relevant clarification questions rather than answering a vague brief.
2. Compare alternatives.
3. Give a justified recommendation.
4. Revise its advice when constraints change.

---

## B. What BlueCallom states about Intelligence-over-Code

Single source, retrieved and re-verified on 2026-09-18:
**<https://bluecallom.com/intelligence-over-code-method/>**

Quoted phrases below are BlueCallom's wording from that page. Our reading of them is section C
and is never mixed in here.

### B1. The core hierarchy

The method's governing principle is **"Prompt is King"** and **"Code is a subordinate of the
King."** The page describes IoC as "far more than just an AI development method. It is the very
foundation of the Native Enterprise AI solution design."

### B2. What the prompt is

The prompt communicates with the model "in a natural and meaningful way," and the model
"understands the meaning of the prompt based on the model's respective level, training, state,
and design."

### B3. What code is used for

Code serves "API Access, Deep Learning algorithms, numerical processing, sending specific data to
a database, and many more activities." Such code functions are "triggered by a prompt" rather
than operating independently, and "none of these activities ... is ever intelligent, autonomous,
or reasoned about."

### B4. IoC is not no-code

Stated explicitly on the page: **"IoC has nothing to do with 'No-Code'; we do use code whenever it
is an advantage, except for convenience."**

### B5. Orchestration vocabulary

The page refers to "agent orchestration," "task orchestration," "prompt-driven interactive flow,"
"Large Action Models (LAM)," and to solutions handling "workflows" and "Intelligent Processes."
It does not define a fixed sequence of steps.

### B6. Claimed benefits

"With better models, we get better responses without needing to change a single line of code."
The page further claims the method handles enterprise complexity without conventional software
limitations, enables autonomous processes that "learn or adjust based on external changes,"
improves understanding of data quality beyond format compliance, and enhances productivity
measurement.

### B7. What the page does **not** state

Verified explicitly during review, because it matters for section C:

- **No mention of testing, validation, schemas, execution limits, or control mechanisms.** The
  page is silent on these. Everything this repository does about schema enforcement, iteration
  caps and state integrity is therefore **our engineering judgement, not a BlueCallom
  requirement**, and is labelled as such in C4.
- No step-by-step development lifecycle, no prompt file format, no required model vendor, and no
  reference architecture for an implementation outside BlueCallom's own platform.

### B8. Platform features we do not reproduce

BlueCallom's related material describes its AgenticBlue framework and GPTBlue Studio, including
a central multi-agent communication strand, a connector protocol between agents, long-horizon
memory, and human oversight checkpoints. We have no access to that platform. We implement the
**method** as stated on the source page above, not the platform, and we do not borrow its product
vocabulary to describe our own components.

---

## C. Our interpretation and implementation choices

### C1. Product framing

A single-purpose advisor, not a general chatbot. The manager brings a portfolio of candidate AI
initiatives and a set of constraints. The application returns a justified, comparative
recommendation that survives a change of constraints.

**Product name: AI Initiative Advisor.** Confirmed by the project owner.

### C2. Advisory actions, not a fixed pipeline

Diagnosis, clarification, comparison, recommendation and revision are **advisory
responsibilities**, each with its own prompt and its own representation in the interface. They
are **not** a mandatory five-step sequence.

The model decides which advisory action is appropriate given the current session context. A
well-specified brief may go straight to comparison. A vague one may need clarification twice. A
constraint change after a recommendation leads to revision. A manager who supplies two
initiatives and no objectives gets asked about objectives, not handed a comparison.

This is our reading of B5, which uses orchestration language without prescribing a sequence, and
of B1, under which deciding *what to do next* is exactly the kind of judgement that belongs in a
prompt. Hard-coding the order in Python would put the central process decision in the subordinate.

### C3. What prompts own

- Which advisory action to take next, and why.
- Which clarification questions are decision-critical.
- Which criteria matter for this manager's situation.
- How to interpret a trade-off.
- What to recommend, and how to justify it.
- How to explain a change of advice.

### C4. What code owns, and why this is not a violation

Code enforces the following, unconditionally. The model cannot waive any of them.

| Control | Enforced by code |
|---|---|
| **Schema** | Every model response is parsed into a declared contract. Malformed output is repaired once, then surfaced as an error. Never rendered unvalidated. |
| **Execution limits** | Maximum advisory actions per session, maximum model calls, timeouts, maximum context size. A loop cannot run unbounded because a prompt decided to continue. |
| **State integrity** | Session state is written only through validated transitions. History is append-only, so a revision can be compared against what preceded it. |
| **Tool contracts** | The set of actions a prompt may select from is fixed in code. A response naming an unknown action is rejected, not improvised around. |

**This is our interpretation, not a BlueCallom instruction.** B7 records that the source page says
nothing about validation or limits. We consider these controls compatible with IoC because they
are not business logic: they decide nothing about which initiative is better. They are the
"precision" case that B4 explicitly reserves for code. Removing them to reduce the Python line
count would be method theatre, and would make the application unsafe to demonstrate.

### C5. Comparison is qualitative and explained, not scored

**No weighted numerical scoring in the MVP.** Removed at the project owner's direction.

A comparison presents each initiative through five distinct, separately labelled categories:

| Category | Meaning |
|---|---|
| **Stated facts** | What the manager actually told us, attributable to their input |
| **Assumptions** | What the advisor assumed in order to proceed, flagged as such |
| **Missing evidence** | What is not known and would change the assessment if supplied |
| **Feasibility constraints** | Budget, timeline, skills, dependencies and regulatory limits that bound the option |
| **Trade-offs** | What is given up by choosing this option over the alternatives |

The recommendation must be traceable to these categories. A justification that cites an assumption
must say so.

**An unknown is never converted into a zero, a low score, or a neutral midpoint.** Silence about
data quality is not evidence of poor data quality. Unknowns propagate into the output as unknowns.

If numerical scoring is proposed in a later iteration, it will require explicitly documented
scales, explicitly documented weights, and a written statement of its limitations, including what
it cannot represent. It will not be introduced implicitly.

### C6. Clarification behaviour

- **At most three questions at a time**, each one decision-critical. A question that would not
  change the advice is not asked.
- The manager may answer any subset, or skip.
- **Skipped and unanswered questions remain visible** in the interface and in the exported brief,
  as either an open unknown or an explicit assumption the advisor has made in order to proceed.
  They are not dropped, and the advisor does not quietly proceed as though they were answered.

### C7. Fictional demonstration data

Fictional organisations only, each with objectives, constraints and a set of candidate
initiatives. No employer data, no real operational data, no BlueCallom platform access, no
customer material. Every sample scenario is labelled as sample data in the interface.

### C8. Offline fixture mode

The application runs without a model API key by replaying recorded fixture responses, so it can
be reviewed by someone with no credentials.

Two rules govern it:

1. Fixture responses are **explicitly labelled as sample data in the interface**, never presented
   as live model output.
2. **A failed live model call is never silently replaced by a fixture.** A failure surfaces as a
   failure. Offline mode is entered deliberately through configuration, not as a fallback.

### C9. Acceptance criteria

1. Changing a prompt file changes the advice, with no Python edit.
2. Changing one constraint produces a revision that names which conclusions moved, which held,
   and why.
3. Every recommendation is traceable to the five categories of C5, with assumptions labelled.
4. The application asks rather than guesses when it lacks decision-critical information, and never
   converts an unknown into a value.
5. Model output failing schema validation is repaired once, then surfaced. Never silently rendered.
6. Execution limits hold even when a prompt requests further action.

---

## D. Decisions

### D-a. Confirmed by the project owner

| Decision | Setting |
|---|---|
| Interface and documentation language | English |
| Working product name | AI Initiative Advisor |
| Offline fixture mode | Yes, explicitly labelled as sample data |
| Fixture as fallback for a failed live call | Never |
| Deployment | Local execution only. No hosting, no Docker at this stage |
| Frontend | React, Vite, TypeScript |
| Backend | Python, FastAPI |
| Numerical scoring in MVP | Removed |
| Clarification questions per turn | Maximum of three |

### D-b. Still open

| # | Decision | Status |
|---|---|---|
| D1 | Runtime model provider | **Deliberately open** until available API access is confirmed. The model client is written behind an interface so this does not block the skeleton or the interface work. |
| D5 | Session persistence | In-memory or JSON file per session. Recommendation: JSON file, since it survives a restart and adds no dependency. |
| D6 | Export formats | Recommendation: Markdown and JSON in the MVP. PDF deferred. |
| D7 | Test depth | Recommendation: unit tests for schema validation, state transitions and limit enforcement, plus one end-to-end run against fixtures. Model judgement is not asserted on. |
| D8 | Response streaming | Recommendation: not in the MVP. |

---

## E. Out of scope for the initial build

Hosting and deployment, Docker, authentication, multi-tenancy, a database, PDF export,
integration with GPTBlue Studio or any BlueCallom API, multi-agent parallelism, cross-session
memory, and languages other than English.
