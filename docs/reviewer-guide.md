# Reviewer guide

A short route through AI Initiative Advisor for an assessor. Setup is in the
[README](../README.md). Everything here refers to files in this repository.

---

## 1. What you are looking at

- **Parts 2 and 3 of the assessment** are demonstrated by this application, which was newly built
  for the assessment from 2026-09-18. Part 2 is the strategy-consulting application; part 3 is its
  interface and the rationale in [ui-ux.md](ui-ux.md).
- **Part 1** asks for one application the candidate built previously. It is supplied separately and
  is not in this repository.

**Who did what.** The project owner set direction, made the product decisions, reviewed each stage
and wrote the development instructions. ChatGPT supported requirements analysis and the preparation
of those instructions. Claude, through Claude Code, implemented the application and wrote the
documentation under the project owner's direction.

## 2. Two kinds of prompt

| Directory | What it is |
|---|---|
| [`backend/prompts/`](../backend/prompts/) | **Runtime prompts.** Loaded from disk on every model call. They are the application's judgement |
| [`docs/prompts/`](prompts/) | **Development prompts.** The instructions given to Claude Code to build the application, saved verbatim and in order, with outcomes in [worklog.md](worklog.md) |

Each runtime prompt starts with YAML front matter declaring its id, version, role, inputs, outputs
and constraints, which follows the prompt structure BlueCallom's method page asks for.

### The runtime prompts, briefly

- **Selector** (`actions/next-action.md`). Chooses what the advisor does next, from the actions the
  code currently permits: diagnose, request context, ask questions, compare, recommend, or wait
  for the manager. There is no fixed pipeline; the order is the selector's decision.
- **Clarification** (`actions/clarify.md`). Asks at most three questions, each stating what its
  answer would change. Never re-asks an answered or skipped question.
- **Comparison** (`actions/compare.md`). Sets every initiative out under five separate headings:
  stated facts (citing the brief or an answer), assumptions (no sources), missing evidence,
  feasibility constraints and trade-offs. No scores. An unknown goes into missing evidence, never
  into a weak assessment.
- **Recommendation** (`actions/recommend.md`). One stance per initiative, in priority order, with
  rationale, the assumptions it holds only if, risks, first actions, every skipped or unanswered
  question as an open unknown, and a note on how far to trust it.

Also: `actions/diagnose.md` (gaps, contradictions and unstated assumptions in the brief),
`actions/request-context.md` (for a brief too thin to work with), `system/advisor.md` (standing
rules for every call) and `support/repair-output.md` (one attempt to fix output that failed
validation).

What code enforces around them (schemas, limits, state, permitted actions) is in
[architecture.md](architecture.md), section 5.2.

---

## 3. Route A — review without any model call

About twenty minutes. No key needed, nothing is charged.

1. **Read the runtime prompts** in `backend/prompts/`, starting with `actions/next-action.md` and
   `actions/recommend.md`.
2. **Read how code bounds them:** `backend/app/core/advisory.py` (the loop),
   `backend/app/core/validation.py` (the single boundary before state),
   `backend/app/core/limits.py` (per-turn ceilings).
3. **Run the tests** (commands in the README). They use deterministic doubles in place of the
   model.
4. **Start the application without a key** (`npm run dev`). The status chip says **Not
   configured**. The sample brief loads, and you can open the brief editor, edit, cancel and apply.
   Pressing **Start advisory session** returns a clear "not configured" error and sends no request.
5. **Read the design rationale** in [ui-ux.md](ui-ux.md), and what was observed in live runs in
   [worklog.md](worklog.md) (entries for prompts 007, 010 and 011).

This route does not show the completed advice on screen. There is no offline mode: the prepared
browser states used during development were review tooling, not a feature of the product, and
development screenshots are not in the repository.

---

## 4. Route B — a live walkthrough

Needs your own OpenAI key in `.env` (README, step 3). **Each session calls the OpenAI API and may
incur charges**; recorded sessions on this brief were estimated at about three to nine US cents
each with `gpt-5-mini`. The model's questions and advice vary between runs, so yours will differ
from the recorded run described here.

The recorded run below is session `2a60d8040351` from the development environment. It is evidence,
not a demo link: it existed only in that machine's backend memory and **cannot be opened on
yours**.

### Step 1 — give the brief a staffing figure (optional, recommended)

The sample brief deliberately leaves headcount empty. The recorded run filled it in first:

1. Select **Review or edit the full brief**. The editor opens in the main column.
2. Under **Constraints**, in **headcount**, enter:

   > We can allocate a total of 0.7 full-time equivalents over the next three months: the
   > operations director at 20% of a full-time working week, one dispatcher at 10%, and our only
   > IT analyst at 40%. These allocations total 70% of one full-time role. We have no data
   > engineer and no previous AI project experience. Work beyond this internal capacity would
   > require an external contractor; contractor availability and funding are not confirmed.

3. Try **Cancel and return** once: the sidebar still says *Not stated*. Open the editor again,
   re-enter the text, and select **Apply changes**. Nothing is sent to the advisor.

### Step 2 — start, and answer in three different ways

Select **Start advisory session**. In the recorded run the advisor asked three questions:

| Question, as generated (shortened where marked …) | What was done |
|---|---|
| Is the 'about 150,000 EUR for the first year' budget confirmed in writing and available to spend on external contractors or licences before November? … | **Skipped** |
| Can we procure and fund an external contractor (data engineer / ML contractor) before November if needed, and roughly how many contractor days could be authorised … between now and the board review? | **Left blank** |
| What historical operational data exists, in what form, and how far back: specifically shipment records with pickup/dropoff timestamps, geolocation/GPS traces, driver logs, and scanned customs documents? … | **Answered** (below) |

The answer given:

> Shipment records with pickup and delivery timestamps go back about four years in our transport
> management system, roughly 9,000 deliveries a month. GPS traces exist only for the last 14
> months and cover about 45 of our 60 vehicles. Driver logs are still on paper. Scanned customs
> documents are kept as PDFs in a shared folder, around 400 a week. All of it sits in our own
> Frankfurt data centre, so customer addresses never leave the EU.

Do the same with whichever questions your run asks: answer one, tick **Skip this question** on
another, leave a third blank, then **Send answers**. If the advisor pauses after its diagnosis,
select **Continue**. The recorded run paused there too; its browser had been closed, so that turn
was sent through the API with the same request the button sends.

### Step 3 — read the advice

In the recorded run: *Customs document extraction* was recommended, *Route optimisation assistant*
was marked consider later, and *Customer service chatbot* was marked not enough information,
because the brief does not describe it.

| Look for | Where |
|---|---|
| The recommendation, and the assumptions it holds only if | Decision overview, the lead card |
| **First actions** | "See first actions" on the lead card (5 in the recorded run) |
| **Evidence** each recommendation cites, with identifiers | "Evidence & sources" on the lead card |
| The skipped and blank questions, labelled differently | "Confirm before committing" |
| Every other open unknown | "Review the other open questions" (8 in the recorded run) |
| **Assumptions** kept apart from facts, and what is not known | Reasoning & sources → How the options compare (assumptions have a dashed rule and a tag) |
| Your answer shown back, with a caveat that answered does not mean checked | Reasoning & sources → What you told the advisor |
| Risks and how far to trust the advice | Reasoning & sources → The advice, in full |
| Prompt versions, content hashes and token usage | `GET /api/sessions/{id}/trace` |

Things worth checking: the skipped question is never cited as a source; nothing you declined to
answer has become a weakness of an option; identifiers such as `Q-HISTDATA` in the advisor's
sentences are shown as readable labels (hover for the identifier).

### Step 4 — change the brief after advice exists

1. Open **Review or edit the full brief**, change any value, and select **Apply changes**.
2. The advice is withdrawn from view and the page says **Your brief has changed.** Nothing has been
   started. The one primary action is **Start a new advisory session**; starting it is your
   choice, and costs a new session.
3. **Discard the changes and return to the previous advice** restores it. Applying an unchanged
   draft, or cancelling, never withdraws anything.

The application does not revise advice within a session. That was planned and not built.

### Step 5 — reopen by URL

Your session's identifier is in the address bar (`?session=…`). Reload the page: the advice
returns with a one-line **Session restored** status, fetched with one `GET` and nothing
regenerated. Restart the backend and reload: the page says the session is **unavailable**,
because sessions are held in memory only.

---

## 5. How to weigh the evidence

| Kind | What it shows | What it does not |
|---|---|---|
| **Live runs** (five, listed in the README) | How the prompts behaved on this brief with `gpt-5-mini` | That they behave the same way every time; each is one execution |
| **Backend tests** (169 at `d55e12f`) | Contracts, limits, state, failure handling and prompt loading, with deterministic doubles | Anything about the quality of the model's judgement |
| **Frontend tests** (15 at `d55e12f`) | Reference rendering and draft-editing rules | Rendering in a browser |
| **Scripted browser checks** | Layout, states, focus and interaction at three viewports, by reopening `2a60d8040351` or serving prepared payloads | Model behaviour; use by a person; screen readers |

Two points to keep separate:

- **The coherent 0.7 FTE demonstration** (`2a60d8040351`) is not the earlier run `40879adc7c67`,
  whose staffing answer said about 1.5 FTE while its own components added to 0.7. The advisor did
  not notice that inconsistency. Correcting the demonstration data changed the input, **not** the
  advisor's ability to detect contradictions.
- **The visual reference** used for the interface was a static design preview whose copy was
  condensed from the fictional example. It was not advisor output.

---

## 6. How the method is interpreted

BlueCallom's page (<https://bluecallom.com/intelligence-over-code-method/>) sets the hierarchy
"Prompt is King" / "Code is a subordinate of the King", says IoC "has nothing to do with
'No-Code'", publishes a prompt structure (role, inputs, expected outputs, constraints), and
describes a procedure in which ChatGPT drafts the prompts and they are built into an agent in
GPTBlue Studio.

This project is a standalone application. It **does not use GPTBlue Studio** or any BlueCallom
platform feature. It applies the method this way:

- The advisory judgement (what to do next, what to ask, how to compare, what to recommend) is in
  the runtime prompts, written in the published structure.
- Code does what prompts should not: calling the API, validating output against schemas, bounding
  each turn, and keeping the manager's answers and session state intact. **These controls are our
  engineering choices.** The BlueCallom page does not require them, and none of them decides which
  initiative is better.

Full reasoning: [requirements.md](requirements.md), sections B and C.

---

## 7. Limitations

Sessions in memory only; no export; no offline mode; no revision within a session; no hosting or
Docker; no screen-reader verification; tested on Windows only; arithmetic inside the manager's own
input is not checked.
