# Prompt 010 — Replay Provenance, Wording and Stance Semantics, and the Final Live Run

- **Date received:** 2026-09-19
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)
- **Language note:** the project owner asked for explanations in Spanish. Interface text, repository
  documentation and runtime prompts remain in English.

The text below is the instruction exactly as received.

---

Complete the remaining review items and perform one final live browser walkthrough.

Keep repository documentation, development prompt records, runtime prompts, and UI text in English. Explain progress to me in Spanish.

Save this instruction verbatim in the next available numbered file under docs/prompts/. Do not retroactively save the previous operational screenshot instructions.

1. Establish the provenance of the replayed screenshots.

The latest screenshots contain different questions and recommendations from the earlier walkthrough:

* The skipped question previously concerned the board-review date; the latest one concerns budget approval.
* The chatbot previously showed NOT ENOUGH INFORMATION; the latest replay shows NOT RECOMMENDED.

Inspect the recorded payloads and replay scripts. Identify which original execution supplied each screenshot set, using available session identifiers, timestamps, filenames, and model traces.

Different recordings are acceptable, but identify them accurately. Do not describe them as the same session or attribute their content differences to frontend changes.

If the original provenance cannot be established, state that explicitly. Preserve the existing captures and historical results; do not reconstruct missing evidence or silently alter payloads.

2. Correct the waiting message.

Replace "This can take up to a minute" everywhere it describes the current interface, including visible messages and accessible announcements, with:

"The advisor is working. This may take a few minutes."

The configured turn deadline is not a guaranteed response time. Keep the loading indicator beside the submission control and retain duplicate-submission protection.

Correct current documentation that presents one minute as a guaranteed maximum. Preserve historical prompt records.

3. Clarify the recommendation semantics in the runtime prompts.

Review how the existing stances are chosen:

* insufficient_information: the available evidence does not support assessing the initiative adequately.
* not_recommended: supplied evidence supports a substantive reason against pursuing it.
* consider_later: there is a supported reason to defer its priority.

Missing information alone must not automatically become evidence that an initiative is bad. The advisor may explain that work should not begin until a gap is resolved while still describing the initiative as insufficiently assessed.

Apply this distinction through the relevant runtime prompts. Do not hard-code a chatbot-specific outcome, impose a fixed ranking, relabel generated results in the frontend, or add another model call to judge the recommendation.

Retain the separation between facts, assumptions, and unknowns.

4. Verify the changes locally.

Run the relevant existing backend tests, frontend type check, and production build.

Record the exact code revision and runtime prompt versions used for the final walkthrough. Make the changes reviewable in Git before testing against the provider.

5. Run one final live browser session.

Use the real application and existing local OpenAI configuration. Remove or disable replay interception for this walkthrough. Do not expose credentials.

Use a 1366 × 768 viewport and the fictional sample scenario.

Read the actual generated clarification questions before answering. Provide a short, coherent fictional answer that directly addresses one question and remains consistent with the brief. Do not reuse a fixed document-volume answer regardless of what was asked.

If three questions appear, answer one, skip another, and leave the third blank. If the advisor chooses a different path, record what actually happens without manufacturing the expected sequence.

Complete one session through the normal UI. Do not launch additional sessions to obtain better wording or prettier screenshots. If it fails, preserve the failure and report it without starting another paid run.

Check that submitted answers remain visible, unresolved information stays explicit, and any recommendation rests on a current comparison.

6. Capture and report the final evidence.

Save readable screenshots of the initial screen, actual questions and entered answer, loading state, submitted-question states, recommendation, and uncertainties.

Use a new folder:
`.local-review/screenshots/final-live/`

Preserve earlier screenshots. Confirm the new files remain ignored and untracked. Keep full traces and temporary browser tooling outside tracked content.

Report the actual action sequence, elapsed time, request and repair counts, available token usage, and estimated cost. Identify missing usage rather than treating it as zero. Distinguish this live execution from earlier replay-based visual checks.

Update the worklog and relevant documentation with the provenance findings, changes, and observed results. Commit and push the code and documentation to the same verified repository and branch. Do not commit screenshots, raw traces, credentials, or temporary tooling.

Finish in Spanish with:

* Published commit.
* Replay provenance findings.
* Final live-run outcome and any remaining limitations.
* Absolute screenshot folder path and filenames.
* The actual question answered and the fictional answer supplied.

Leave the real application running and stop for review.
