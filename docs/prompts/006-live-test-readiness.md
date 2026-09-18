# Prompt 006 — Live Test Readiness

- **Date received:** 2026-09-18
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)

The text below is the instruction exactly as received.

---

Before the first live test, address the following findings from the published commit a19dce9260d47d9136a0a9496e2ed48e9f8fb00a.

Save this instruction verbatim as `docs/prompts/006-live-test-readiness.md`. Keep this iteration focused on the existing flow.

1. CONFIGURATION STATUS

`Settings.model_configured` currently accepts any non-empty provider/key pair, including the committed placeholder.

Use consistent local configuration checks for the health endpoint and client creation. Reject empty values, known placeholders and unsupported providers. Do not impose a brittle API-key format.

Describe this status as local configuration presence, not successful authentication. Only a completed provider request establishes connectivity.

2. ENFORCE THE TURN DEADLINE

`budget.check_time()` runs between iterations. A selector, action or repair request can cross the deadline and still commit output.

Enforce the remaining wall-clock budget around awaited work, cancel overdue operations and prevent late commits. Ensure timeout handling releases the session lock and leaves a usable session status.

3. PRESERVE THE COMPLETE EXECUTION TRACE

`TurnResult.traces` is not persisted, while the trace endpoint reads only advisory records. Selector usage disappears, clarification records have no usage, and repair usage is omitted from persisted records.

Persist attempt-level traces separately from accepted advisory outputs. Include selector, action and repair attempts, their prompt hashes, outcome and provider-reported usage when available. Preserve completed attempts even when a later step fails.

Never invent token counts for failed or cancelled requests. Mark unavailable usage explicitly.

4. PROTECT ANSWER UPDATES

The answers endpoint calls `session.record_answers()` outside the session lock. It can therefore modify answers while another turn is awaiting a model response.

Serialize answer updates with advisory execution using one clear locking arrangement. Avoid nested-lock deadlocks and ensure results cannot be committed against answers different from those used to generate them.

5. CORRECT THE SCHEMA EXPLANATION

Re-check the current official Structured Outputs documentation:
https://developers.openai.com/api/docs/guides/structured-outputs

The blanket assertion that pattern, string-length bounds, array-length bounds and numerical bounds are universally unsupported is too broad; the documentation distinguishes additional restrictions for fine-tuned models.

The conservative wire layer may remain. Correct its rationale and distinguish our chosen subset, local schema checks and actual service acceptance. Do not claim that local conversion proves OpenAI accepted a schema.

VERIFICATION

Add focused regression tests for placeholder configuration, an in-flight deadline overrun, trace completeness including repairs, and overlapping answer submission/advisory execution.

Run the relevant tests and existing build checks. Do not add features.

Update current documentation and the worklog without rewriting historical prompts. Commit and push to the confirmed repository, then report the commit and results.

The project owner will configure the key locally and perform the first live user-flow test. Keep live verification marked pending until it actually occurs.
