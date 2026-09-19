# Interface and interaction design

This document explains the interface decisions for assessment part 3. It describes the interface
as built after prompt [013](prompts/013-visual-redesign.md). Earlier iterations and the reasons
they changed are in the [worklog](worklog.md).

The reader is an operations or general manager deciding which AI initiative to fund first. They are
not a data scientist. They have a board meeting coming, limited time, and no reason to trust a tool
that sounds more certain than it is. Every decision below follows from that.

---

## 1. Layout

Two columns inside a frame capped at 1280 px.

- **Sidebar, 204 px.** The manager's own context: organisation, what matters, the limits they
  gave, and the options on the table. The start control sits directly under the organisation name,
  so it is visible without scrolling at 1366 × 768. The full brief editor is one control away
  ("Review or edit the full brief") rather than always open, because once the brief is written
  the manager reads it far more often than they edit it.
- **Main column.** Whatever the session needs attention on now. Before a session it explains what
  will happen and that nothing runs until the manager starts it. While a clarification round is
  open, the questions come first, so the manager is never scrolling past an empty advice panel to
  reach what is being asked of them. Once advice exists, the decision brief takes the column.

The header carries the product name, the organisation and one honest status chip (Checking…,
Ready, Not configured, Not connected). Diagnostics sit behind that chip rather than on the page:
they matter to whoever runs the service, not to the person deciding.

## 2. Hierarchy of the decision brief

The completed view answers three questions in order, and the visual weight falls in the same order.

1. **What should I do?** The advisor's summary, set large, then a lead card for each initiative the
   advisor recommends: a white card with a 3 px green top edge, its stance, its name, the
   rationale, what it is based on, and the conditions it holds only if.
2. **What else was considered?** The other initiatives in quieter two-column cards, each with its
   stance and rationale and a disclosure for what it rests on.
3. **What must I check before committing?** Questions the manager skipped or left unanswered,
   shown as rows with a restrained amber edge, then a counted disclosure for every other unknown
   the advisor flagged. Then how far to trust the advice.

**No ranking is invented.** The recommendation is a list, and array order is not a priority. A
"Recommended first" label would claim an ordering the advisor never stated, so it does not appear.
Several recommended initiatives all get lead cards. None recommended produces an explicit
"Nothing is recommended yet" card rather than promoting the least bad option.

## 3. Progressive disclosure

The overview shows what a manager needs to decide. Everything that supports it is one step away,
never removed.

- **Reasoning & sources** is a second tab holding the full diagnosis (gaps, contradictions,
  unstated assumptions), the comparison criteria and each initiative's entry, every answer the
  manager submitted, the risks and the confidence statement.
- **First actions** open under the lead card on request. They are the next step, not the decision.
- **"Why this recommendation"** is a neutral text link that switches to the reasoning view. It is
  deliberately not a button, so it does not compete with the decision itself.
- **Counts on every disclosure.** A closed section says how many items it holds, so hiding
  something never hides that it exists.

## 4. How uncertainty is shown

The advisory contract keeps evidence, assumptions and unknowns apart (see
[architecture](architecture.md) §3). The interface keeps them visibly apart too.

- **What you told us** is plain text with a solid rule.
- **What the advisor assumed** is marked with a dashed rule and an assumption tag.
- **Not known** is listed separately and never drawn as a low value or a zero.
- **Conditions** a recommendation depends on sit inside its card, in a soft green panel headed
  "Holds only if", not in a footnote.
- **Skipped and unanswered** questions keep distinct labels ("You skipped this", "Not answered")
  because they mean different things: one is a choice, the other a gap.
- **Outdated advice** is kept for reference under an amber notice saying it no longer reflects what
  the advisor knows, rather than being deleted or presented as current.

Amber is used only for these things. Green is the accent and marks the recommended path. Nothing
uses red, because nothing on the page is an error the manager caused.

## 5. Readable references, identifiers kept

The model cites sources by identifier (`OBJ-COST`, `Q-HISTDATA`). The interface resolves each to
what the manager recognises: "Objective · Lower the administrative cost per shipment", or "Your
answer" with the question text. The identifier stays in the tooltip, so a reviewer can still trace
it. A reference that does not resolve is shown as its raw identifier rather than dropped.

## 6. States

| State | What the manager sees |
|---|---|
| Initial | The brief in the sidebar, the start control, and a statement that nothing runs yet |
| Editing | The full brief as auto-growing fields; if a session exists and the brief changes, a note that starting again creates a new session and does not revise the current advice |
| Starting, sending, continuing | The pressed control disabled with its label changed, a spinner beside it, and "The advisor is working. This may take a few minutes." Duplicate submissions are blocked |
| Questions pending | The round first in the main column, each question with why it matters, a free-text answer and "Skip this question" |
| Paused without advice | "In progress", a Continue control, and the reasoning so far |
| Completed | The decision brief, as above |
| Outdated | The previous advice under an amber notice, and Continue |
| Error or timeout | A notice saying whether the step can be retried, with technical detail folded away and a Dismiss control |
| Reopened by URL | A notice that the session was reopened as the advisor left it and nothing was regenerated |
| Session unavailable | A notice that sessions are held in memory and lost on restart, and one control to load the sample brief. Nothing starts |

## 7. Visual system

Colour, type and geometry are tokens in `frontend/src/styles/tokens.css`.

- **Colour.** Page `#F5F6F4`, surfaces `#FFFFFF`, text `#192D29`, secondary text `#596B65`,
  borders `#DDE5DF`, accent `#116B54` on `#FFFFFF`, soft accent `#EDF6F0`, warning text `#795617`
  on `#FAF3E5`, hover `#EEF1ED`. Text and secondary text both pass WCAG AA on white and on the page
  colour.
- **Type.** Body 14 px / 1.55. Page title 29 px, semibold, tight tracking. Recommendation summary
  25 px / 1.25. Section headings 14 px semibold. Secondary text 12–13 px, metadata no smaller than
  11 px.
- **Geometry.** Lead card 11 px radius and 23 px padding; secondary cards 9 px radius, 17 px
  padding, 12 px gaps; controls 7 px radius. Main column padding 28 px.
- **Icons** are inline outline SVGs, hidden from assistive technology, so there is no icon font and
  no external request.

## 8. Responsive behaviour

- **1366 × 768** is the design target. The start control is above the fold.
- **1440 × 900 and wider.** The frame stops at 1280 px and centres, so line lengths stay readable.
  Long prose is capped in width inside cards.
- **Below 1100 px** the sidebar narrows to 188 px and the main padding tightens.
- **Below 860 px, including 390 × 844.** The layout stacks: sidebar context first, then the main
  column. Cards become single-column, controls grow to 40 px touch targets, and the header drops
  the organisation name. Verified with no horizontal overflow.

## 9. Accessibility

- Focus is always visible on controls. Headings that receive focus from code, so a screen reader
  lands on new content, show no ring because they are not controls.
- A polite live region announces when work starts, when questions arrive and when advice is ready.
- Tabs expose `aria-current`; the brief toggle exposes `aria-expanded`; status is never carried by
  colour alone.

## 10. Known limits

- **No persistence.** A reopened URL works only while the backend process holds the session.
- **No export** of the decision brief.
- **Checked in one browser engine** (Chromium, through Playwright) at three viewports. Not tested
  with a screen reader.
- **Long constraints are cut to four lines** in the sidebar. The full text is in the tooltip and in
  the brief editor.
