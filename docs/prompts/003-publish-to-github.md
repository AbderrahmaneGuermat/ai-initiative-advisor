# Prompt 003 — Publish to GitHub

- **Date received:** 2026-09-18
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)

The text below is the instruction exactly as received.

---

I have created the public GitHub repository. This is the confirmed destination:

https://github.com/AbderrahmaneGuermat/ai-initiative-advisor

Publish the existing local project there.

1. Save this message verbatim in `docs/prompts/`, using the next available sequential number. Preserve existing records.
2. Verify that the authenticated GitHub account is `AbderrahmaneGuermat`. If another account is active or authentication is unavailable, stop and explain what I need to do.
3. Inspect the local repository and remotes. If `origin` already points somewhere else, report that before changing it.
4. Check tracked files and commit history for credentials or confidential material. Keep `.env`, dependency folders and build output excluded.
5. Commit the new prompt record and configure `origin` as:
   https://github.com/AbderrahmaneGuermat/ai-initiative-advisor.git
6. Push the current branch and its existing history, setting its upstream. Preserve the existing commits and branch name. Do not force-push.
7. Verify that the remote contains the expected files and matches the local commit. Record the successful publication in the worklog, commit and push that update.

Do not create another repository or implement additional features.

Return the repository URL, published branch, final commit hash and verification results. Then stop for review.
