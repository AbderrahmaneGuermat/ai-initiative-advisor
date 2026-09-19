# Prompt 013 — Approved Visual Redesign

- **Date received:** 2026-09-19
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)
- **Language note:** code, interface text and repository documentation remain in English.

The text below is the instruction exactly as received.

---

Implement the approved visual redesign of AI Initiative Advisor in the existing application. Match the design specification below closely, including its proportions, typography, colours, spacing and information hierarchy.

This is an implementation task. Complete the redesign, verify it in a real browser, capture the results and publish through the established repository workflow.

1. Scope and starting point

The latest reported revision is 8423047bf552085fea8d4cb0dff15e576e4ab68e. Inspect the current working tree and branch before making changes; preserve any subsequent work.

Keep React, Vite, TypeScript and the existing backend integration. Reuse the current session state and API contracts.

This iteration concerns presentation and interaction. Preserve the advisory behaviour, runtime prompts, validation, freshness checks and provider configuration. No paid model calls are authorised for this task.

Save this development instruction verbatim under the next available number in docs/prompts/, following the existing convention. Update the relevant design documentation and worklog accurately.

2. Visual direction and exact design tokens

The approved concept is a restrained enterprise interface with a compact white context sidebar, a soft neutral page background and one visually prominent recommendation.

Use these light-theme tokens:

* Page background: #F5F6F4
* Surface: #FFFFFF
* Primary text: #192D29
* Secondary text: #596B65
* Borders: #DDE5DF
* Primary accent: #116B54
* Text on primary buttons: #FFFFFF
* Soft accent background: #EDF6F0
* Warning text: #795617
* Warning background: #FAF3E5
* Hover background: #EEF1ED

Use Inter if already available locally; otherwise use "Segoe UI", system-ui, sans-serif. Do not require an external font request.

Typography:

* Body: 14px, line-height approximately 1.55.
* Main page heading: 29px, weight 600–650, line-height 1.2, slightly tight letter spacing.
* Main recommendation heading: 25px, weight 600–650, line-height 1.25.
* Organisation name: 18px.
* Section headings: 14px, semibold.
* Secondary copy and controls: 12–13px.
* Small metadata: 11px minimum.
* Small section labels may use uppercase with modest letter spacing.

Geometry:

* Header padding: 18px vertically and 24px horizontally.
* At approximately 1024px wide, use a 204px sidebar and a flexible main column.
* Sidebar padding: approximately 27px vertically and 20px horizontally.
* Main content padding: 28px.
* Keep the desktop content frame comfortable at larger widths, approximately 1280px maximum.
* Main recommendation: white surface, 1px border, 3px green top edge, 11px corner radius and 23px internal padding.
* Secondary option cards: 9px radius, 17px padding and a 12px gap.
* Primary buttons: 7px radius, approximately 9px × 13px padding.
* Use thin borders and generous spacing, with little or no shadow.

Use small, consistent outline icons. Reuse the existing icon solution, or add a lightweight icon dependency if needed. Avoid decorative charts, gradients, oversized illustrations and invented metrics.

3. Application shell and context sidebar

Header:

* Left: a small green rounded brand mark with a compass-style icon, followed by "AI Initiative Advisor".
* Right: the organisation name and a compact, truthful service status.
* Keep technical diagnostics available without making them the main header content.
* Do not include the mockup-only labels "Design preview", "Presentation concept" or "No model calls" in the application.

Sidebar:

* "Your organisation", followed by the organisation name.
* "What matters", followed by the actual objectives.
* Compact sections for budget, internal capacity, target and data constraints.
* A clearly labelled control to review or edit the full brief.
* Preserve access to every editable field and the existing start/start-again behaviour.

The reference scenario contains a roughly €150,000 unconfirmed budget, 0.7 FTE, a November board review and EU address-data constraints. These are example values, not constants to embed in components.

Use existing structured content. Where a short value is unavailable, display the supplied text with wrapping or accessible expansion. Do not introduce semantic extraction heuristics just to populate a decorative summary.

Before a session starts, the primary start action must be visible without scrolling on a 1366×768 screen.

4. Completed recommendation view

Use the following hierarchy:

* Small label: "Your decision brief".
* Heading: "A focused place to start."
* Short description referring to the actual number of initiatives.
* Two understated navigation controls with an underline for the active view:
  "Decision overview" and "Reasoning & sources".

Decision overview:

A. The recommendation

Give the recommended initiative the prominent white card with the green top edge.

Show its actual disposition, initiative name, rationale, relevant supporting information and conditions. Conditions must remain visible close to the advice.

In the approved example, this is customs document extraction. The reference shows approximately 400 documents per week and an existing EU-hosted source. Show such facts only when the session supports them and their provenance remains available.

Include:

* "See first actions": reveals the existing first actions.
* "Why this comes first", or appropriately neutral wording when priority is not explicit: opens the reasoning view.

Do not infer a ranking from array order. Use "Recommended first" only when the advice actually establishes that priority. Support multiple recommended initiatives and cases with no recommended initiative.

B. Other initiatives

Show the remaining initiatives in quieter cards, two columns when space permits.

Each card contains its disposition, name and rationale. Preserve the distinction between "Consider later", "Not recommended" and "Not enough information".

The reference contains route optimisation and a customer service chatbot, but the layout must work with the actual session content.

C. Unresolved information

Use the heading "Confirm before committing".

Keep skipped and unanswered questions visible with their distinct statuses. Present them as concise rows with restrained amber accents rather than large repetitive yellow panels.

Additional uncertainties may use progressive disclosure with a clearly labelled control and count. Preserve their full content and provenance. Do not silently merge or discard similar-looking statements.

Avoid presenting raw identifiers such as Q-HISTDATA or INI-ROUTE as primary labels. Where a valid mapping exists, display the readable question or initiative name, while keeping the original reference accessible in the evidence detail.

5. Reasoning and all other application states

"Reasoning & sources" must provide access to the complete diagnosis, comparison, submitted answers, supporting references, assumptions, risks and confidence caveats.

Use readable sections and expandable details. Preserve the distinction between user-provided information and the advisor's interpretation. Do not replace the existing records with hardcoded summaries from this specification.

The redesign must also cover:

* Initial brief and editing.
* Starting a session.
* Pending clarification questions.
* Sending answers.
* A completed clarification round.
* A pause with Continue available.
* Current and outdated recommendations.
* Provider errors and timeouts with retained results.
* Restoring a session through ?session=<id>.
* An unavailable session and explicit sample-brief recovery.

While questions need an answer, make the active form easy to reach; an empty recommendation panel must not push it far down the page.

Keep the loading indicator beside the initiating control, prevent duplicate submissions and preserve the distinction between question status and a round awaiting response.

Navigation between views, expanding details and reopening a session must not call the model.

Keep every user control functional. Preserve full content without truncating important text. Maintain keyboard navigation, visible focus, accessible status announcements and status labels that do not rely on colour alone.

6. Responsive behaviour

Match the approved desktop composition first.

At intermediate widths, reduce padding and allow the sidebar to narrow modestly. At narrow widths, stack the layout and keep the current task prominent, with an obvious route to the context.

Secondary cards should become a single column. Text and labels must wrap without horizontal scrolling. Maintain comfortable touch targets.

Check at least:

* 1366×768
* 1440×900
* 390×844

7. Browser verification and screenshots

Use the real browser to inspect the rendered application and exercise the interactions.

If session 2a60d8040351 remains in the running backend, reopen it through the existing URL mechanism and use it for the completed-state review. Avoid restarting that backend unnecessarily, since its sessions are in memory.

If it is unavailable, use the existing local recorded responses through the established replay approach. Clearly distinguish replay from a live backend. Do not generate another paid session or manufacture model output.

Verify the initial state, editing, questions, loading, completed recommendation, reasoning view, session recovery and unavailable-session state. Use deterministic fixtures for states the available session cannot demonstrate.

Run the existing relevant checks and add focused coverage only where changed interaction logic creates a concrete regression risk.

Save screenshots in a new directory:

.local-review/screenshots/ui-redesign-001/

Capture the initial view, expanded context, clarification form, sending state, decision overview, expanded first actions, reasoning, unresolved information, unavailable-session state and mobile view. Record which source produced each state.

Open the screenshots and inspect them. Correct clipping, awkward wrapping, weak contrast and spacing problems before finishing.

Keep screenshots, raw session responses and temporary browser tooling outside tracked Git content. Preserve earlier review material and verify the local exclusion.

8. Completion

Update the UI/UX rationale to explain the new hierarchy, progressive disclosure, responsive behaviour and treatment of uncertainty.

Create a reviewable commit and publish using the established workflow. Before pushing, verify the authenticated GitHub account, branch and destination:

AbderrahmaneGuermat/ai-initiative-advisor

Preserve unrelated changes and do not force-push.

Report:

* What changed visually and behaviourally.
* Any necessary departures from the approved design.
* Browser checks and their results.
* Which screenshots used the live backend or replay.
* Screenshot directory.
* Commit and publication status.
* Any remaining limitations.

Proceed through implementation and verification. The goal is a close visual match to the approved concept, integrated with the working application.
