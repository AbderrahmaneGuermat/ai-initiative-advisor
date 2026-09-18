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

## Attribution

The instructions in this directory were written by the project owner, with ChatGPT supporting
requirements analysis and prompt preparation. Claude, via Claude Code, acted on them.
