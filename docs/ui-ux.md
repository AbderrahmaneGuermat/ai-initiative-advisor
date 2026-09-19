# Interface and interaction design

This document explains the interface decisions for assessment part 3. It describes the interface
as built after prompts [013](prompts/013-visual-redesign.md) and
[014](prompts/014-visual-refinement.md). The visual reference was a static design preview with
fictional content; the application renders real session data in its proportions. Earlier
iterations and the reasons they changed are in the [worklog](worklog.md).

The reader is an operations or general manager deciding which AI initiative to fund first. They are
not a data scientist. They have a board meeting coming, limited time, and no reason to trust a tool
that sounds more certain than it is. Every decision below follows from that.

---

## 1. Layout

Two columns inside a frame capped at 1280 px.

- **Sidebar, 204 px.** Session controls first: the organisation, the start control, and "Review or
  edit the full brief" directly beneath it. The editor opens there, next to the button it affects.
  Below that, a summary of the context: objective titles, the constraints as ruled rows (their
  real kind as the label, their full value beneath), and the options on the table. Why each
  objective matters lives in the full brief, not in the summary.
- **Main column.** Whatever the session needs attention on now. Before a session it explains what
  will happen and that nothing runs until the manager starts it. While a clarification round is
  open, the questions come first. Once advice exists, the decision brief takes the column.

The header carries the product name, the organisation and one honest status chip (Checking…,
Ready, Not configured, Not connected). Diagnostics sit behind that chip: they matter to whoever runs
the service, not to the person deciding.

## 2. Hierarchy of the decision brief

One large heading per screen region, and the largest thing inside the content is the
recommendation.

1. **Page head.** A small eyebrow with the initiative count, the page title, and the advisor's own
   summary as the page description, in full, at body size (14 px, 1.6 line height). It frames the
   reading; it is not a second headline.
2. **What should I do?** A lead card for each initiative the advisor recommends: a white card with a
   3 px green top edge, its stance, **the initiative's name at 25 px**, the rationale, and the
   conditions it holds only if. Then the actions: a green **See first actions** button, a
   **Why this recommendation** link to the reasoning, and **Evidence & sources** with a count.
3. **What else was considered?** The other initiatives in quieter two-column cards: a plain stance
   label, the name, the rationale, and a disclosure for what each rests on and cites.
4. **What must I check before committing?** The skipped and unanswered questions as rows in one
   ruled list, each with its status in words, then "Review the other open questions" with a count.
   Then how far to trust the advice.

At 1366 × 768 the recommended initiative's name and its primary action are both visible without
scrolling.

**No ranking is invented.** The recommendation is a list, and array order is not a priority. A
"Recommended first" label would claim an ordering the advisor never stated, so it does not appear.
Several recommended initiatives all get lead cards. None recommended produces an explicit
"Nothing is recommended yet" card rather than promoting the least bad option.

## 3. Progressive disclosure

The overview shows what a manager needs to decide. Everything that supports it is one step away,
never removed.

- **Conditions stay visible.** What a recommendation holds only if is decision-critical, so it is in
  the card, in the warning colour, above the actions.
- **Provenance is one step away.** "Evidence & sources" lists every source the recommendation cites:
  what kind of thing it is, what it says, and its identifier. The reasoning view lists the same for
  every claim.
- **First actions** open under the card on request. They are the next step, not the decision.
- **Reasoning & sources** is the second tab: the answers given, the reading of the brief, the
  comparison with evidence, assumptions and unknowns kept apart, the risks and the confidence.
- **Counts on every disclosure.** A closed section says how many items it holds, so hiding
  something never hides that it exists.

## 4. How uncertainty is shown

The advisory contract keeps evidence, assumptions and unknowns apart (see
[architecture](architecture.md) §3). The interface keeps them visibly apart too.

- **What you told us** is plain text with a solid rule.
- **What the advisor assumed** is marked with a dashed rule and an assumption tag.
- **Not known** is listed separately and never drawn as a low value or a zero.
- **Conditions** a recommendation depends on sit inside its card under "Holds only if".
- **Skipped and unanswered** questions keep distinct labels ("You skipped this", "Not answered")
  because they mean different things: one is a choice, the other a gap.
- **Outdated advice** is kept for reference under an amber notice saying it no longer reflects what
  the advisor knows, rather than being deleted or presented as current.

Amber is used only for these things. Green is the accent and marks the recommended path. Nothing
uses red, because nothing on the page is an error the manager caused.

## 5. Readable references, identifiers kept

The model cites sources by identifier and also writes identifiers into its sentences:
"in-house (Q-HISTDATA)", "map to OBJ-COST". Both are made readable.

- **In prose**, an identifier that exactly matches something this session holds is drawn as what it
  refers to, with a dotted underline: an objective's statement, an option's name, "budget
  constraint", "your answer" for an answered question, and the opening words of the question in
  quotation marks for one that was skipped or not answered. The identifier stays on the element
  and in its tooltip.
- **In source lists** ("Evidence & sources", the reasoning view) each reference shows its kind, its
  readable label and its identifier.
- **Nothing is guessed.** A token that does not resolve exactly (a context identifier, a look-alike,
  a longer identifier that merely contains a known one) is printed as written.
- **Nothing is changed.** Only rendering differs. The stored model output is untouched, and the
  segments always rejoin to the original text; `frontend/tests/references.test.mjs` checks this.

## 6. Long values

A constraint can be a paragraph. In the sidebar it is cut to three lines with a **Show all** button
beneath it. The button appears only when the text is actually cut, works by keyboard and touch, and
announces its state. The full value is also in the brief editor. A tooltip is never the only way
to read it.

## 7. States

| State | What the manager sees |
|---|---|
| Initial | The context in the sidebar, the start control, and a statement that nothing runs yet |
| Editing | The full brief as auto-growing fields, opened under the start control; if a session exists and the brief changes, a note that starting again creates a new session |
| Starting, sending, continuing | The pressed control disabled with its label changed, a spinner beside it, and "The advisor is working. This may take a few minutes." Duplicate submissions are blocked |
| Questions pending | The round first in the main column, each question with why it matters, a free-text answer and "Skip this question" |
| Paused without advice | "In progress", a Continue control, and the reasoning so far |
| Completed | The decision brief, as above |
| Outdated | The previous advice under an amber notice, and Continue |
| Error or timeout | A notice saying whether the step can be retried, with technical detail folded away and a Dismiss control |
| Reopened by URL | A compact notice that the session was reopened as the advisor left it and nothing was regenerated |
| Session unavailable | A notice that sessions are held in memory and lost on restart, and one control to load the sample brief. Nothing starts |

## 8. Visual system

Colour, type and geometry are tokens in `frontend/src/styles/tokens.css`.

- **Colour.** Page `#F5F6F4`, surfaces `#FFFFFF`, text `#192D29`, secondary text `#596B65`,
  borders `#DDE5DF`, accent `#116B54` on `#FFFFFF`, soft accent `#EDF6F0`, warning text `#795617`
  on `#FAF3E5`, hover `#EEF1ED`. Text and secondary text both pass WCAG AA on white and on the page
  colour.
- **Type.** Body 14 px / 1.55. Page title 29 px, semibold, tight tracking. Recommended initiative
  25 px / 1.25. Section headings 14 px semibold. Secondary text 12–13 px, metadata no smaller than
  11 px.
- **Geometry.** Lead card 11 px radius and 23 px padding; secondary cards 9 px radius, 17 px
  padding, 12 px gaps; controls 7 px radius. Main column padding 28 px.
- **Icons** are inline outline SVGs, hidden from assistive technology.

## 9. Responsive behaviour

- **1366 × 768** is the design target. The start control, the recommended initiative's name and
  "See first actions" are above the fold.
- **1440 × 900 and wider.** The frame stops at 1280 px and centres. Prose is capped in width.
- **Below 1100 px** the sidebar narrows to 188 px and the main padding tightens.
- **Below 860 px, including 390 × 844.** The sidebar keeps only its controls in view: organisation,
  start, "Review or edit the full brief" and **Show context**. The context folds behind that
  disclosure, so the active task follows immediately: the introduction before a session, the
  questions during a round, the decision once advice exists. The summary folds to three lines
  with "Show all". Cards become single-column and controls grow to 40 px touch targets. Verified
  with no horizontal overflow in the initial, clarification and completed states.

## 10. Accessibility

- Focus is always visible on controls. Headings that receive focus from code, so a screen reader
  lands on new content, show no ring because they are not controls.
- Every disclosure is a button or `<details>` with its state exposed (`aria-expanded`), including
  "See first actions", "Evidence & sources", "Show all" and "Show context". The primary action was
  verified reachable and operable by keyboard alone.
- A polite live region announces when work starts, when questions arrive and when advice is ready.
- Status is never carried by colour alone.

## 11. Known limits

- **No persistence.** A reopened URL works only while the backend process holds the session.
- **No export** of the decision brief.
- **Checked in one browser engine** (Chromium, through Playwright) at three viewports. Not tested
  with a screen reader.
- **Real content is longer than the reference's.** The reference used short, invented copy
  ("0.7 FTE", "About €150,000"). The application shows the brief's actual values and the model's
  actual sentences, so its cards and sidebar rows are taller. No shorter values are invented or
  extracted to imitate it.
