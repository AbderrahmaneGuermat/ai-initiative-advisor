# Prompt 012 — Reopening an Existing Session

- **Date received:** 2026-09-19
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)
- **Language note:** the project owner asked for explanations in Spanish. Code, interface text and
  repository documentation remain in English.

The text below is the instruction exactly as received.

---

Add the smallest frontend change needed to reopen an existing backend session, then capture the completed corrected example without making any new model requests.

Keep code, UI text, and repository documentation in English. Explain progress in Spanish. Save this instruction verbatim in the next available numbered file under docs/prompts/.

1. Preserve the existing session first.

Before restarting or changing anything, fetch:
GET /api/sessions/2a60d8040351
GET /api/sessions/2a60d8040351/trace

Save both responses in the ignored local review directory. Record the current provider-attempt count.

Keep the backend process running. Its sessions are in memory, and restarting it would lose the session we need.

If the session is already unavailable, report that immediately. Do not create another paid session or present a replay as recovery from the live backend.

2. Implement lightweight session recovery.

The backend already provides GET /api/sessions/{session_id}. Add the corresponding frontend client function.

Support opening the application with a session query parameter, for example:
http://localhost:5173/?session=2a60d8040351

On startup, load that session and restore its brief, questions, comparison, recommendation, and existing status information.

Prevent the default sample-scenario request from overwriting a restored brief.

When a newly created session is returned by the API, update the URL with its identifier so that refreshing or reopening that URL can recover it while the backend still holds it.

Do not hard-code the example session ID in application code.

Loading an existing session must perform GET requests only. It must never automatically start a session, submit answers, or invoke Continue.

If the backend returns 404, show a clear message that the session is unavailable and may have been lost after a backend restart. Offer an explicit way to start again without automatically making a model request.

This is recovery of in-memory state, not persistence across backend restarts. Document that distinction. Do not add a database or change the advisory workflow.

3. Verify the actual recovery.

Use Playwright with the real application at 1366 × 768.

Open the corrected session through its URL, reload the page, and reopen that URL in a fresh browser context. Confirm that the same session and its completed recommendation appear.

Check that the restored brief contains 0.7 FTE and that comparison and recommendation remain current.

Inspect network requests and compare the provider-attempt count before and after. It must remain unchanged.

Check the missing-session path without disturbing the real session. Run frontend type checking and the production build.

4. Capture the missing evidence.

Save readable screenshots of the restored staffing constraint, recommendation, uncertainties, and a full-page view under:
.local-review/screenshots/final-coherent-restored/

Preserve all earlier screenshots. Confirm the new files remain ignored and untracked.

Describe these accurately as the current frontend displaying an already completed live session fetched from the real backend. They are not a new model execution.

5. Publish and report.

Update the worklog and startup documentation. Commit and push the frontend and documentation changes to the same verified repository and branch. Keep screenshots and raw responses out of Git.

Report in Spanish:

* Published commit.
* Whether session recovery and reload worked.
* Session ID and provider-attempt counts before and after.
* Absolute screenshot folder path and filenames.
* Remaining limitations.

Leave the real backend running. Make no new paid model requests.
