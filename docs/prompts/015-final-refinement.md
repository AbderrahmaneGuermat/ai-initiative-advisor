# Prompt 015 — Final UI Refinement and Verification

- **Date received:** 2026-09-19
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)
- **Language note:** code, interface text and repository documentation remain in English.

The text below is the instruction exactly as received.

---

Complete one final UI refinement and verification pass for AI Initiative Advisor.

The latest reported commit is 46c4469. Inspect the current branch and working tree first and preserve subsequent work.

The visual direction is approved. Keep the current colours, typography, recommendation layout and information hierarchy. Address the remaining usability issues below, fix any concrete regressions discovered, and bring this iteration to completion.

Record this instruction verbatim under the next available number in docs/prompts/.

1. Move the brief editor into the main content area

The current editor renders inside the 204px sidebar. This makes long inputs difficult to read and edit while the main content area remains largely empty.

When “Review or edit the full brief” is selected:

* Show the editor in the main content area, with a comfortable maximum width of approximately 760px.
* Keep the sidebar as a compact context summary on desktop.
* Use the available width on mobile.
* Provide a clear “Edit your brief” heading.
* Organise organisation, situation, objectives, constraints and initiatives into readable sections.
* Use full-width multiline fields for long text. Preserve all existing fields and identifiers.
* Provide clearly labelled controls to apply changes or cancel and return.

Inspect the current editing and session behaviour before implementing this. Preserve its guarantees:

* Opening, closing or cancelling the editor must not create a session, call the model or alter the saved session.
* Use local draft state so cancelled edits do not change the brief.
* Applying an unchanged draft must not invalidate the current advice.
* Applying changed input must follow the existing explicit new-session behaviour. Explain that the changed brief requires a new advisory session.
* Starting that session must remain a separate, deliberate user action.
* Never display the previous advice as current advice for the changed brief.
* Preserve access to the original session through its existing URL.
* Switching views must preserve any unsent clarification answers.

Move focus appropriately when opening and closing the editor. Preserve visible keyboard focus and an intuitive tab order.

Do not introduce backend persistence or a revision workflow.

2. Make the restored-session notice more discreet

The restored-session banner currently occupies substantial space, particularly on mobile, and prominently displays an internal identifier.

Replace it with a compact inline status such as “Session restored”, with an accessible detail explaining that existing results were loaded and nothing was regenerated.

Keep the identifier available in details or diagnostics. It does not need to appear in the primary message.

This change applies only to successful restoration. Keep unavailable-session errors, outdated-advice warnings and provider errors prominent and actionable.

Do not imply that restoring a session makes outdated advice current or that sessions survive a backend restart.

3. Final usability pass

Inspect the actual rendered interface and correct any concrete problems directly related to this refinement:

* Labels, long values and buttons wrapping awkwardly.
* Form fields that are clipped or unnecessarily narrow.
* Missing or confusing return controls.
* Duplicate controls or competing primary actions.
* Focus lost when switching between editing and advice.
* Mobile controls that are difficult to tap.
* Broken disclosures, reference links or unavailable-session recovery.

In a completed session, keep restarting visually secondary to reviewing the advice and its first actions. Preserve an obvious way to start again.

Retain full access to evidence, assumptions and uncertainty. Do not simplify the presentation by deleting information, inventing summaries or changing model output.

Keep this pass bounded. Do not add new product features, dependencies, animations, runtime prompt changes or another visual direction unless a concrete defect makes a small change necessary.

4. Verification without model calls

No paid model calls are authorised.

Use the existing backend session where available and clearly labelled prepared states where needed. Preserve the running backend and its in-memory sessions where possible.

Verify in a real browser:

* Open the editor from the initial screen.
* Open it from a restored completed session.
* Edit a long field, cancel, and confirm the original brief and advice remain unchanged.
* Apply an unchanged draft and confirm the current recommendation remains current.
* Apply changed input and confirm the UI clearly requires an explicit new-session action.
* Confirm editing and navigation alone make no provider calls.
* Return between the editor, decision view and reasoning view.
* Preserve pending answer drafts when visiting the editor.
* Confirm keyboard navigation and mobile usability.
* Confirm restored, unavailable and outdated session states remain distinct.

Intercept any test action that would start a model run before it reaches the backend. Do not restart the advisor to obtain better screenshots.

Check at 1366×768, 1440×900 and 390×844.

Run the frontend typecheck, production build and relevant existing tests. Add focused tests for draft cancellation, unchanged edits or other new state transitions where needed. Broaden testing only to address a concrete remaining risk.

5. Screenshots and completion

Save a fresh set under:

.local-review/screenshots/ui-final/

Include:

* Desktop editor with a long field visible.
* Mobile editor.
* Completed desktop recommendation with the compact restored-session status.
* Completed mobile recommendation.
* The state after applying a changed brief, before starting a new session.

Open and inspect the screenshots. Keep screenshots, raw responses and temporary review tooling excluded from Git. Preserve previous review sets.

Update the UI/UX rationale and worklog, distinguishing live-backend presentation from prepared states.

Commit and push through the established workflow after verifying the authenticated account, destination and branch:

AbderrahmaneGuermat/ai-initiative-advisor
master

Do not force-push.

Finish with a concise report covering:

* What changed.
* Editing and cancellation behaviour.
* Verification results and whether any model calls occurred.
* Screenshot location and provenance.
* Commit and publication status.
* Any specific issue that still prevents delivery.

Complete the implementation and review rather than returning another plan.
