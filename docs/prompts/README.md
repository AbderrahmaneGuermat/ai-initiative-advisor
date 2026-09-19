# Development prompt record

This directory is the chronological record of the instructions that produced this repository.
Each file holds one development instruction, saved verbatim, before it was acted on.

These are **development prompts**. They are not the prompts the application executes. The
application's runtime prompts will live in `backend/prompts/` once implementation begins, and the
two are never mixed.

## Conventions

- One file per instruction, numbered in order: `001-`, `002-`, and so on, with a short slug.
- The instruction text is reproduced exactly as received, below a horizontal rule. The metadata
  header above that rule is the only addition.
- Files are never edited after the fact. A correction is a new entry.
- Nothing in this directory is reconstructed, summarised or invented. If an instruction was not
  given, there is no file for it.
- The outcome of each prompt is recorded separately in [../worklog.md](../worklog.md), which
  references the prompt by number.

## Index

| # | File | Instruction |
|---|---|---|
| 001 | [001-project-brief.md](001-project-brief.md) | Project brief: organise the repository, document requirements, propose an implementation plan, do not implement |
| 002 | [002-design-review-and-skeleton.md](002-design-review-and-skeleton.md) | Design review corrections: assessment scope, adaptive orchestration, qualitative comparison, confirmed choices; then implement the skeleton only |
| 003 | [003-publish-to-github.md](003-publish-to-github.md) | Publish the existing local repository to the confirmed public GitHub destination, verifying account, remotes and absence of secrets first |
| 004 | [004-data-contracts-and-foundations.md](004-data-contracts-and-foundations.md) | Correct five documentation inconsistencies, implement the Pydantic data contracts, add one fictional worked example, and test the contract boundaries |
| 005 | [005-openai-advisory-flow.md](005-openai-advisory-flow.md) | Integrate OpenAI, implement the runtime prompts, the bounded advisory loop, the validation boundary and a working interface |
| 006 | [006-live-test-readiness.md](006-live-test-readiness.md) | Fix five findings before the first live test: configuration status, the turn deadline, trace completeness, answer locking, and the schema explanation |
| 007 | [007-live-run-corrections.md](007-live-run-corrections.md) | Record the first live run and correct what it found: timeout continuity, skipped-question references, advisor sequencing, and usage measurement |
| 008 | [008-state-consistency.md](008-state-consistency.md) | State consistency: a recommendation requires a current comparison, history is kept but labelled, and a pending round is distinguished from an unanswered question |
| 009 | [009-interface-improvements.md](009-interface-improvements.md) | Interface work from the browser walkthrough: primary action reachable, progress beside the control, readable hierarchy, and the manager's submitted answers shown back |
| 010 | [010-provenance-and-final-live-run.md](010-provenance-and-final-live-run.md) | Establish replay provenance, correct the waiting message, clarify stance semantics, and run the final live browser session |
| 011 | [011-staffing-consistency-correction.md](011-staffing-consistency-correction.md) | Correct the staffing inconsistency in the demonstration data and verify it with one live session |
| 012 | [012-session-recovery.md](012-session-recovery.md) | Reopen an existing backend session from a URL, and capture the completed example without new model requests |
| 013 | [013-visual-redesign.md](013-visual-redesign.md) | Implement the approved visual redesign with exact tokens, cover every state, verify at three viewports, and document the interface rationale |
| 014 | [014-visual-refinement.md](014-visual-refinement.md) | Refine the redesign against the attached reference: hierarchy, a simpler recommended card, a compact sidebar, mobile reading order, readable references in prose, and a corrected prepared screenshot |
| 015 | [015-final-refinement.md](015-final-refinement.md) | Move the brief editor into the main column as a draft, make the restored-session notice discreet, and complete a final usability and verification pass |

## Attribution

The instructions in this directory were written by the project owner, with ChatGPT supporting
requirements analysis and prompt preparation. Claude, via Claude Code, acted on them.
