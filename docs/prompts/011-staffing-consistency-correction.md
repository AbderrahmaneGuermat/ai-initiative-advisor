# Prompt 011 — Staffing Consistency Correction and Verification

- **Date received:** 2026-09-19
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)
- **Language note:** the project owner asked for explanations in Spanish. Repository documentation
  and interface content remain in English.

The text below is the instruction exactly as received.

---

Complete the final example-data correction and verification. Keep the scope limited to the staffing inconsistency identified by the reviewer.

Keep repository documentation and UI content in English. Explain your results to me in Spanish. Save this instruction verbatim in the next available numbered file under docs/prompts/.

1. Inspect the previous execution.

Locate the saved outputs for session `40879adc7c67`, tested against revision `8f0c184`.

Read the complete diagnosis, particularly its contradictions and uncertainty findings. Establish whether it explicitly identified the mismatch between the stated 1.5 FTE and the staffing breakdown.

Assuming a five-day working week:

* One day per week = 0.2 FTE.
* Half a day per week = 0.1 FTE.
* 40% of one full-time role = 0.4 FTE.
* Total = 0.7 FTE, not 1.5.

Report what the actual output says. If the saved output is unavailable, state that detection could not be verified.

Append a correction to the worklog explaining that the submitted fictional answer addressed the question but contained an internal numerical contradiction. Preserve the original execution, screenshots, traces, and historical entries.

2. Prepare one internally consistent demonstration.

Use the same fictional organisation and initiatives. Before starting the new session, populate the existing staffing constraint in the brief with this text:

"We can allocate a total of 0.7 full-time equivalents over the next three months: the operations director at 20% of a full-time working week, one dispatcher at 10%, and our only IT analyst at 40%. These allocations total 70% of one full-time role. We have no data engineer and no previous AI project experience. Work beyond this internal capacity would require an external contractor; contractor availability and funding are not confirmed."

Entering this in the brief ensures that the advisor receives the corrected capacity without depending on which clarification questions it chooses.

Document that staffing was supplied in the brief. Do not describe it as a clarification answer unless the advisor actually asks for further staffing information and receives one.

3. Perform one live browser walkthrough.

Use the real application and existing OpenAI configuration, with replay interception disabled, at 1366 × 768.

Read the actual clarification questions. Answer one coherently, skip another, and leave another blank if three are offered. Do not paste the staffing text into an unrelated question or force a particular question sequence.

Complete one session through the normal interface. Check that the recommendation and comparison are current and that any staffing quantity used is consistent with 0.7 FTE.

Do not modify runtime prompts, application logic, or generated outputs to obtain a preferred result. If the run fails or introduces another inconsistency, preserve and report it rather than starting another paid session.

4. Preserve the evidence.

Save new screenshots under:
`.local-review/screenshots/final-coherent/`

Capture the staffing constraint, submitted clarification responses, recommendation, and remaining uncertainties. Keep all earlier captures intact.

Verify that screenshots and raw traces remain ignored and untracked. Record the session ID, tested revision, exact inputs, action sequence, available usage, and outcome.

This run verifies the corrected example. It does not demonstrate improved contradiction detection, because no such model-behaviour change was made.

5. Close the iteration.

Update the development prompt record and worklog, then commit and push those documentation changes to the same verified repository and branch. No application changes or broad test reruns are required for this task.

Report in Spanish:

* Whether the previous diagnosis detected the contradiction.
* The new session ID and outcome.
* The staffing quantity actually reflected in the advice.
* Published commit.
* Absolute screenshot folder path and filenames.
* Any remaining limitation.

Leave the real application running and stop for review.
