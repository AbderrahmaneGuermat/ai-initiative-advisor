# Prompt 009 — Interface Improvements from the Browser Walkthrough

- **Date received:** 2026-09-19
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)
- **Language note:** the project owner asked for explanations in Spanish. Interface text, repository
  documentation and runtime prompts remain in English.

The text below is the instruction exactly as received.

---

Implement a focused UI/UX improvement based on the screenshots from the browser walkthrough.

Keep interface text, repository documentation, and runtime prompts in English. Explain progress to me in Spanish. Save this development instruction verbatim in the next available numbered file under docs/prompts/. Do not retroactively save the previous operational screenshot instruction.

1. Make the primary action easy to find.

The initial Start advisory session button is below the entire context form. Make starting the sample scenario possible without scrolling through every field.

Keep the context accessible through clearly labelled sections and a compact summary. Preserve editing and the existing distinction between starting a new session and continuing one.

Use multiline or automatically expanding controls where objectives, constraints, and descriptions are currently clipped.

2. Show progress where the interaction happens.

When the manager submits answers, show a loading label and indicator beside the submission control, within the visible area. Provide an accessible status announcement and prevent duplicate submissions.

Use only progress information the application actually knows. Do not invent completion percentages or intermediate stages.

When questions or a recommendation arrive, make the new content easy to locate through appropriate focus management or a clear navigation control.

3. Establish a readable information hierarchy.

Keep the executive summary, all initiative stances, and important uncertainties easy to scan. Put detailed diagnosis findings, comparison evidence, assumptions, and supporting explanations in clearly labelled expandable sections.

Preserve access to the complete content and sources. Do not merely truncate text or hide uncertainty.

Give the recommendation sufficient reading width. Adapt the layout for laptop screens rather than forcing three narrow, fully expanded columns. Avoid adding empty space merely to equalise panel heights.

Move technical version and build-stage information out of the main manager-facing header and into diagnostics. Keep operational errors visible and actionable.

4. Show what the manager actually submitted.

Display the submitted answer text alongside its question and status after the round closes. Extend the API view minimally if necessary.

Preserve the distinction between response submission and whether the requested information was supplied. An answered status must not imply that the content was verified or that every information gap was resolved.

The walkthrough answered a staffing-capacity question with document-volume information. Keep that execution documented honestly: the volume was supplied, while staffing capacity remained unknown. Do not invent a staffing answer or alter historical results.

5. Verify the presentation.

Use the available Playwright setup to inspect the interface at 1440 × 900 and 1366 × 768. Check initial actions, long field content, loading feedback, settled questions, and recommendation readability.

Reuse the existing session or locally recorded responses where possible. Clearly distinguish replay-based visual checks from live model execution. Do not start additional paid sessions in this iteration.

Preserve existing screenshots. Save new numbered screenshots in a separate subfolder under the already ignored `.local-review/screenshots/`. Confirm they remain untracked.

Run the relevant existing tests, frontend type check, and build. Update the worklog with what was actually observed and what remains unverified.

Commit and push the application changes and development documentation to the same verified repository and branch. Keep screenshots and temporary browser tooling out of Git.

Report the commit, verification results, and local screenshot paths, then stop for review.
