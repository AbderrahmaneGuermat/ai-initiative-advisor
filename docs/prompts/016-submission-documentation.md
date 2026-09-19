# Prompt 016 — Submission Documentation

- **Date received:** 2026-09-19
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)
- **Language note:** code, interface text and repository documentation remain in English.

The text below is the instruction exactly as received.

---

Prepare the repository for assessment submission by bringing its documentation into line with the completed application.

The implementation and UI are approved. This is a documentation and handover task, not another development iteration.

The reviewed baseline is d55e12fd074199cd805ab24da6c0745d25b516ef. Inspect the current branch and preserve later work.

Record this instruction under the next available number in docs/prompts/.

1. Correct the current-state documentation

Read README.md, docs/requirements.md, docs/architecture.md, docs/ui-ux.md and docs/prompts/README.md against the actual code and latest worklog entries.

The review found these specific inconsistencies:

* README introduction says the application revises recommendations when constraints change, although that workflow is not implemented.
* README says live verification was completed twice, then lists more executions and omits the later coherent example from its main summary.
* README says OpenAI service acceptance has not been observed, contradicting the recorded live runs.
* README still describes browser review as something nobody has done and describes the old three-panel interface.
* README implies editing starts a new session. Editing now creates a local draft; applying changed input requires a separate explicit start action.
* README and the prompt index refer to runtime prompts as something that will exist later.
* Requirements still declare that application logic has not started and describe offline replay and revision as existing capabilities.
* Requirements still list the provider and other resolved decisions as open.
* Architecture contains obsolete descriptions: a health-only API, unwritten prompts, an open provider decision, planned session storage and tests, and implemented-looking export or fixture paths.
* Some package descriptions, configuration comments and dependency comments still describe the skeleton stage.

Correct present-tense descriptions. Clearly distinguish implemented behaviour, deferred features and historical proposals.

Preserve previous numbered prompts and historical worklog entries verbatim. Append corrections where necessary rather than rewriting what happened.

2. Make the README useful to an assessor

Keep the opening concise and organised around:

* What the application does.
* Which assessment parts it addresses.
* How to install, configure and start it.
* How to inspect a session.
* Where to read the runtime prompts, development prompts and UI/UX rationale.
* What was verified and what remains limited.

Include repository cloning before installation. Put local key configuration before the instruction to start an advisory session.

Avoid instructions that overwrite an existing .env. Explain that local configuration status does not authenticate the key and that live advisory requests may incur API charges.

Check commands against the actual package scripts and dependency requirements. Distinguish the runtime requirement from the frontend test-runner requirement. Use the recorded Node 24 environment as a clear reproducible baseline rather than guessing a lower supported version.

State that Windows was tested; do not claim macOS/Linux execution was verified.

Remove the redundant live curl smoke test if the browser walkthrough already provides the same evaluation path.

3. Provide a short assessor walkthrough

Create docs/reviewer-guide.md and link it prominently from the README.

Include:

* Parts 2 and 3 are demonstrated by this newly built application.
* Part 1 asks for one previously built application and is supplied separately.
* The roles of ChatGPT, Claude Code and the project owner, accurately attributed.
* The distinction between docs/prompts/ and backend/prompts/.
* A short explanation of the selector, clarification, comparison and recommendation prompts.
* A guided walkthrough using the actual questions generated, with answered, skipped and unanswered states.
* Where to inspect evidence, assumptions, first actions and uncertainty.
* Draft editing, cancellation, explicit new-session behaviour and URL recovery.
* A route for reviewing the code and design without making model calls.

Do not require the assessor to possess session 2a60d8040351. It is evidence from the development environment, not a portable demo link.

Do not claim that prepared browser states constitute an offline product mode.

4. Keep method attribution precise

Recheck the official source:
https://bluecallom.com/intelligence-over-code-method/

The page includes guidance on prompt roles, inputs, outputs and constraints, along with steps involving ChatGPT and GPTBlue Studio. Avoid a blanket statement that no procedure or prompt-structure guidance is published.

Explain how this standalone implementation interprets the method. Attribute validation, state integrity and execution limits to our engineering choices rather than to an explicit BlueCallom requirement.

Do not claim integration with GPTBlue Studio or use platform features we have not implemented.

5. Present evidence accurately

Use the existing worklog and code as the basis.

* Distinguish live model runs from deterministic tests, prepared browser states and reopening an existing session.
* Keep the coherent 0.7 FTE demonstration separate from the earlier inconsistent 1.5 FTE example.
* State that correcting that example did not improve contradiction detection.
* Attribute test counts to the revision or recorded run; do not imply they were rerun during this documentation task.
* Avoid presenting a single execution’s latency or estimated cost as a general guarantee.
* Preserve uncertainty about the unexplained historical POST.
* Clarify that the visual reference used condensed copy based on the fictional example; it was not an additional live advisor output.

Keep the limitations explicit: in-memory sessions, no export, no offline product replay, no in-session brief revision, no hosting or Docker, and no screen-reader verification.

6. Verify and publish

Check internal links, file paths, command names and consistency across the updated documents. Make sure current summaries no longer contradict one another.

No model calls, UI changes, new features or dependency upgrades are authorised. Existing runtime behaviour must remain unchanged. Small metadata and comment corrections are within scope.

Keep screenshots, raw responses, .env and temporary tools excluded from Git.

Append the worklog entry and update the prompt index. Commit and push through the established workflow after verifying the authenticated account, destination and branch:

AbderrahmaneGuermat/ai-initiative-advisor
master

Do not force-push.

Report the corrected claims, assessor entry point, checks performed and published commit. Identify any actual remaining submission blocker; do not propose another development phase.
