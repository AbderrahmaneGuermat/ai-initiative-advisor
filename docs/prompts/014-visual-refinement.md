# Prompt 014 — Visual Refinement Against the Reference

- **Date received:** 2026-09-19
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)
- **Attachment:** `ai-initiative-advisor-design.html`, a static design preview with fictional
  content. It is not reproduced here; a local copy was kept outside Git for browser comparison.
- **Language note:** code, interface text and repository documentation remain in English.

The text below is the instruction exactly as received.

---

Refine the existing UI redesign to match the attached ai-initiative-advisor-design.html more closely.

The latest reported commit is 99c3010. Inspect the current state first and preserve subsequent changes. This is a focused refinement of the existing implementation.

Open the attached HTML in the browser and inspect its source. Use it as the visual reference for hierarchy, proportions and spacing. Its fictional content and mockup controls are examples; the application must continue rendering actual session data and supporting all existing interactions.

Record this development prompt under the next available number in docs/prompts/.

1. Restore the intended visual hierarchy

In the current screenshots, the full recommendation summary is displayed as a large, multi-line headline above the recommended initiative. It dominates the screen and pushes the actual recommendation down.

Change this:

* The initiative name should be the prominent heading inside the recommended card, approximately 25px.
* Render the overall summary as ordinary body text, approximately 14px with comfortable line spacing.
* Keep the full summary available. It may use an explicitly labelled expandable section if necessary.
* Avoid stacking multiple large headings and a large paragraph before the recommendation.
* Preserve all model-generated wording; do not generate new summaries or truncate content irretrievably.

Match the attached reference’s balance between the page heading, recommended card and secondary options.

2. Simplify the recommended card

The current “Based on” block exposes long question text and numerous source labels before the main actions.

Move detailed provenance into an accessible “Evidence & sources” disclosure or the reasoning view. Keep every reference available.

Keep decision-critical conditions visible beside the recommendation. Additional explanation can expand on demand.

Make “See first actions” and “Why this recommendation” easy to find. The former should have the reference’s green primary-button styling.

Preserve the existing treatment of multiple recommended initiatives and cases with no recommendation. Do not infer a ranking from array order.

3. Make the sidebar genuinely compact

The reference sidebar summarises the context. The implementation currently includes lengthy objective explanations and puts the editor below most of the content.

* Show objective titles in the compact view; move their supporting explanations into the full brief.
* Put “Review or edit the full brief” near the primary session control.
* Preserve the full budget, staffing and other constraint text.
* For long values, provide an explicit keyboard- and touch-accessible expansion.
* A hover tooltip must not be the only way to read a clipped value.
* Keep the existing editor and all editable fields usable.

Use actual structured fields. Do not hardcode “0.7 FTE”, invent concise values, or introduce fragile extraction rules to imitate the mockup.

4. Correct the mobile reading order

The mobile screenshots show the entire context before the decision. A manager must scroll through a long sidebar to reach the result.

On narrow screens:

* Show the active task first: clarification when awaiting answers, or the decision when advice is ready.
* Make context available through a compact, clearly labelled disclosure.
* Keep editing and session controls easy to reach.
* Preserve access to all content and prevent horizontal overflow.

Check the initial, clarification and completed states separately. A mobile layout that works for the final result must also work before a session starts.

5. Finish readable source references

Identifiers such as Q-HISTDATA, OBJ-COST and INI-ROUTE remain visible inside narrative paragraphs.

Use the existing reference lookup to render known identifiers as readable labels or accessible reference links, including when they occur inside prose.

Only transform exact identifiers that resolve against the session. Preserve the original text and identifiers in the evidence detail or underlying data. Leave unresolved references intact rather than guessing their meaning.

Do not remove sources, modify stored model output or change runtime prompts.

6. Correct the screenshot fixture

Screenshot 03 places a delivery-volume answer in the budget-confirmation field. Correct this prepared interaction so the answer addresses the displayed question.

Either place the historical-data answer under its matching question, or use clearly labelled synthetic input that matches the budget question.

Preserve the original session, traces and previous screenshots. Record that the corrected screenshot uses a prepared state. Do not imply that this validates model behaviour.

7. Verify and finish

No paid model calls are authorised. Use the existing backend session for completed-state screenshots if it remains available, and clearly labelled replay or prepared states where needed.

Keep the running backend alive where possible, since its sessions are in memory. Browser navigation, reference expansion and tab changes must not create a session or call the model.

Check the implementation beside the attached reference at 1366×768, 1440×900 and 390×844. Inspect:

* Hierarchy and spacing.
* Visibility of the recommendation and its actions.
* Mobile reading order.
* Complete access to long context values.
* Readable references.
* Keyboard focus and disclosure controls.
* Existing recovery, outdated-advice and clarification behaviour.

Run the frontend typecheck, production build and relevant existing checks. Add focused tests only where new rendering or interaction logic needs coverage.

Save a new screenshot set under:
.local-review/screenshots/ui-redesign-002/

Keep it excluded from Git. Open and inspect the screenshots, and distinguish live-backend presentation from prepared states in your report.

Update the UI/UX rationale and worklog. Commit and push through the established workflow after verifying the account, destination and branch. Do not force-push.

Report the changes, verification results, remaining visual differences, screenshot location and published commit. Complete the refinement without generating another model session.
