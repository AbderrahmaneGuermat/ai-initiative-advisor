# Requirements

Status: **proposed, awaiting review.** Nothing in this document has been implemented yet.

This file separates three different kinds of statement, because conflating them is the easiest
way to fail an assessment of this type:

- **A — What the assessment asks for.** Taken from the assignment as relayed by the project owner.
- **B — What BlueCallom states about Intelligence-over-Code.** Sourced from BlueCallom's own
  public pages, with the source noted. These are constraints on *how* we build, not our inventions.
- **C — Our implementation choices.** Everything else. These are ours to defend, and ours to change.

---

## A. Assessment requirements

| # | Requirement | Source |
|---|---|---|
| A1 | Build a simple strategy-consulting application for managers, with AI assistance | Assignment |
| A2 | Follow BlueCallom's Intelligence-over-Code (IoC) method | Assignment |
| A3 | Explain the prompts used to develop the application | Assignment |
| A4 | Design a sample enterprise AI interface and explain the UI/UX decisions | Assignment |

The project owner has decided that A1, A2 and A4 are satisfied by a single application, and A3
by the development-prompt record in [prompts/](prompts/).

### A1 expanded — what the application must do

Agreed with the project owner in [prompts/001-project-brief.md](prompts/001-project-brief.md):
the application helps a manager prioritise enterprise AI initiatives against their objectives,
resources and constraints. It must:

1. Ask relevant clarification questions rather than answering a vague brief.
2. Compare alternatives.
3. Give a justified recommendation.
4. Revise its advice when constraints change.

These four verbs — **diagnose, clarify, compare, revise** — are the functional backbone of the
product and, per the brief, are to be driven by prompts rather than by branching code.

---

## B. What BlueCallom states about Intelligence-over-Code

Retrieved 2026-09-18 from BlueCallom's public pages. Quoted phrases are BlueCallom's wording.

### B1. The core hierarchy

IoC is described as "far more than just an AI development method. It is the very foundation of
the Native Enterprise AI solution design." Its governing principle is **"Prompt is King"** and
**"Code is a subordinate of the King."**
Source: <https://bluecallom.com/intelligence-over-code-method/>

### B2. What belongs in prompts

Workflow orchestration and task management, business logic and decision-making, process
reasoning, and autonomous decision-making where desired. The prompt "communicates with the AI
(LLM) in a natural and meaningful way"; code by contrast "remains non-intelligent and linear."

### B3. What belongs in code

Code handles "API Access, Deep Learning algorithms, numerical processing, sending specific data
to a database" and similar technical operations triggered by prompts, but "none of these
activities ... is ever intelligent, autonomous, or reasoned about."

### B4. IoC is not no-code

BlueCallom is explicit that IoC "has nothing to do with 'No-Code'"; they "still have thousands of
lines of code, but only for interacting with systems and functions that must be coded for access
or precision." Code is used "whenever it is an advantage, except for convenience."

### B5. A claimed benefit that constrains our design

"With better models, you get better responses without needing to change a single line of code,
and with updated context, a prompt can elicit deeper responses without requiring any code
changes." This is a testable design property, and we treat it as an acceptance criterion. See C7.

### B6. Prompt and agent granularity

BlueCallom's AgenticBlue framework describes agents as composed of "3 to 20 prompts per agent,
depending on the complexity of the task," with prompts sequenced inside an agent and functions
called only when needed: "we use prompts to manage processes and call specific functions only
when needed." Prompts are described as modular and reusable, with defined roles, inputs, outputs
and constraints.
Source: <https://bluecallom.com/new-agentic-ai-framework/>

### B7. Framework concepts we are *not* required to reproduce

The same page describes the **Agentic Spin** (a central communication strand for parallel
multi-agent coordination), a multi-agent protocol with "Pro- and Post-Synaptic" connectors,
stateful long-horizon memory, and **Human Interaction Points (HIPs)**, which are designated human
oversight checkpoints inside otherwise autonomous agents. These are properties of BlueCallom's
own platform, GPTBlue Studio. We do not have access to that platform, so we implement the
*method*, not the platform. Two of these concepts are cheap and genuinely useful to mirror at our
scale, and we propose to do so: Human Interaction Points (C4) and modular prompts with declared
contracts (C3).

### B8. The boundary of what is stated

BlueCallom's public pages state a philosophy and a component vocabulary. They do **not** publish a
step-by-step development lifecycle, a prompt file format, a required model vendor, or a reference
architecture for a non-GPTBlue implementation. Everything at that level of detail in this
repository is ours, belongs to section C, and is labelled as such.

---

## C. Our implementation choices

### C1. Product framing

A single-purpose advisor, not a chatbot. The manager brings a portfolio of candidate AI
initiatives and a set of constraints. The application returns a ranked, justified shortlist that
survives a change of constraints. Working name **AI Initiative Advisor**. See open decision D2.

### C2. The five-stage advisory pipeline

Our reading of A1 plus B6 gives five prompt stages, run in sequence within one advisory session.

| Stage | Purpose | Kind |
|---|---|---|
| 1. Diagnose | Read the stated objectives, constraints and candidate initiatives; identify what is missing, contradictory or unstated | Prompt |
| 2. Clarify | Ask a short set of targeted questions; accept partial or skipped answers | Prompt plus HIP |
| 3. Compare | Evaluate each initiative against derived criteria; produce per-criterion judgements with reasoning | Prompt |
| 4. Recommend | Produce a ranked shortlist, a justification per rank, named risks, and a near-term action sequence | Prompt |
| 5. Revise | On a constraint change, re-evaluate and state explicitly what changed, what did not, and why | Prompt |

Five stages sits inside BlueCallom's stated range of "3 to 20 prompts per agent" (B6). We expect
the real count to land between eight and twelve once the system prompt, the criteria rubric and
the output-repair prompt are included.

### C3. Prompt contract

Every prompt is a version-controlled Markdown file with YAML front matter declaring its
identifier, version, role, inputs, outputs and constraints. This is our concrete rendering of
B6's "defined roles, inputs, outputs, and constraints." Prompts are loaded from disk at runtime
and are not embedded in Python source, so the claim in B5 can actually be exercised: editing a
prompt file changes behaviour without touching code.

### C4. Human Interaction Points

Two in the MVP. The first is after Diagnose, where the manager answers or skips the clarification
questions. The second is after Recommend, where the manager changes a constraint and triggers
Revise. Both are explicit stop-and-wait points, not background autonomy.

### C5. The division of labour, applied

Following B2 and B3.

**Prompts own:** which criteria matter for this manager, how to weight them, what to ask, how to
interpret a trade-off, what to recommend, and how to explain a change of advice.

**Code owns:** model API calls and retries, session state, schema validation of model output,
arithmetic on scores the model has assigned, export rendering, and serving the interface.

Concretely: the model decides that regulatory exposure is a relevant criterion and that a given
initiative scores two out of five on it. Python multiplies and sums. Python never decides a
ranking, and the model is never asked to be a calculator. This is a direct reading of B3, which
places numerical processing in code.

### C6. Fictional data only

Three fictional demonstration scenarios, a mid-size insurer, a logistics operator and a hospital
network, each with objectives, constraints and six to eight candidate initiatives. No real
employer data, no BlueCallom platform access, no scraped customer material.

### C7. Acceptance criteria we hold ourselves to

1. Changing a prompt file changes the advice, with no Python edit.
2. Changing one constraint, such as budget, deadline, headcount or risk appetite, produces a
   revision that names which initiatives moved and why.
3. Every recommendation cites the criteria and the manager's own stated constraints.
4. The application refuses to produce a ranking when it has too little information, and asks
   instead. Silence is not a valid response to a vague brief.
5. Model output that fails schema validation is repaired or surfaced, never silently rendered.

---

## D. Open decisions that need the project owner's input

| # | Decision | Options | Our recommendation |
|---|---|---|---|
| D1 | Model provider | Anthropic Claude, OpenAI, or a provider-agnostic adapter | A provider-agnostic adapter with Claude as the default. It costs one small module and removes a single point of failure at demo time. |
| D2 | Product name | AI Initiative Advisor, or something else | The owner's call. Placeholder in use throughout. |
| D3 | Interface language | English, Spanish, or both | English, assuming the assessment is reviewed in English. Needs confirmation. |
| D4 | Offline demo mode | Yes or no | Yes. A recorded-fixture mode so the application demonstrates without an API key or network. Assessors may not have credentials. |
| D5 | Session persistence | In-memory, JSON file, or SQLite | A JSON file per session. It survives a restart, adds no dependency, and keeps the diff readable in Git. |
| D6 | Export formats | Markdown, JSON, PDF | Markdown and JSON in the MVP. PDF deferred, since it adds a native dependency for little assessment value. |
| D7 | Test depth | Smoke only, schema and scoring unit tests, or end-to-end | Schema validation and scoring arithmetic unit tests, plus one end-to-end run against fixtures. We test the deterministic parts and do not assert on model judgement. |
| D8 | Response streaming | Yes or no | No for the MVP. It complicates state handling for a demo nobody will wait on. |

---

## E. Explicitly out of scope for the initial build

Hosting and deployment, Docker, authentication and multi-tenancy, a real database, PDF export,
integration with GPTBlue Studio or any BlueCallom API, multi-agent parallelism (the Agentic Spin
of B7), long-horizon cross-session memory, and internationalisation beyond D3.
