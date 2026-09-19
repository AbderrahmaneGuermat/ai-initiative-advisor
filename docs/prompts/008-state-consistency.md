# Prompt 008 — State Consistency

- **Date received:** 2026-09-18
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)

The text below is the instruction exactly as received.

---

Address the state-consistency issues below before adding features or running further paid tests.

Keep repository documentation, development prompt records, runtime prompts, and UI text in English. Explain progress to me in Spanish. Save this instruction verbatim in the next available numbered file under docs/prompts/.

1. Require a current comparison before recommending.

In permitted_actions(), recommend is currently available whenever session.comparison exists, even when comparison_is_current() is false.

Only offer recommend when the comparison reflects the current answers. Enforce that prerequisite at the validation or commit boundary as well, so an outdated comparison cannot support a newly accepted recommendation.

Keep diagnosis optional and preserve the adaptive workflow. This is a data-consistency prerequisite, not a mandatory sequence of advisory stages.

Update the selector prompt to explain that new answers require refreshing an outdated comparison before recommending.

2. Preserve history while identifying outdated results.

Keep previous validated outputs in the session history. Expose enough state for the interface to distinguish current results from results awaiting an update.

If new answers make existing advice outdated and the refresh fails or times out, do not display the previous recommendation as current advice. Clearly label its status and allow continuation.

Advance the answers version only when answer content or status actually changes. An identical resubmission must not trigger unnecessary recomputation. Track submission of a clarification round separately from changes to its answers.

3. Distinguish unanswered questions from a pending clarification round.

AdvisoryThread currently uses question.status === "unanswered" to decide whether to show editable questions and the Send answers button.

Use the session's pending-round state to control submission. After the manager submits a round, unanswered questions should remain visible as unknowns without implying that another response is required. Preserve the distinction between answered, skipped, and unanswered.

4. Verify the affected paths.

Use focused deterministic tests to cover:

* A comparison becomes outdated after a genuinely new answer.
* Recommendation cannot be accepted until that comparison is refreshed.
* Continue reuses a current comparison without repeating it.
* An identical answer submission does not invalidate current results.
* A failed refresh preserves history without presenting outdated advice as current.
* Submitting one answer, one skip, and one blank completes the round while retaining all three statuses.

Do not initiate another paid live run in this iteration. Check frontend types and build. If browser interaction is unavailable, explicitly leave visual verification pending.

Update the worklog and relevant decisions, commit, and push to the same verified repository and branch. Report the commit and actual verification results, then stop for visual review.
