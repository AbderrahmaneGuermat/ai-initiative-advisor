# Prompt 002 — Design Review and Skeleton

- **Date received:** 2026-09-18
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)

The text below is the instruction exactly as received.

---

Thanks. The overall direction is suitable. We will continue incrementally.

Save this message verbatim as docs/prompts/002-design-review-and-skeleton.md before making changes. Preserve the existing prompt record and update the worklog with actual outcomes.

First, revise the design documentation with the following corrections.

1. ASSESSMENT SCOPE

This new application addresses assessment parts 2 and 3:

* Build a strategy-consulting application using the IoC method.
* Design and explain its enterprise UI/UX.

Part 1 will describe my existing projects separately. Do not present this newly built application as evidence of earlier professional work.

2. IoC AND ORCHESTRATION

Keep diagnosis, clarification, comparison, recommendation and revision as useful interface concepts and prompt responsibilities.

Do not assume every interaction must follow a fixed five-step pipeline. Prompts should determine the appropriate next advisory action based on the available context.

Code must still enforce schemas, execution limits, state integrity and tool contracts. Do not move these controls into prompts merely to minimise Python.

Review and cite the working official method URL:
https://bluecallom.com/intelligence-over-code-method/

Clearly distinguish the source's statements from our interpretation.

3. COMPARISON AND SCORING

Remove mandatory weighted numerical scoring from the MVP.

Use an explained qualitative comparison that distinguishes:

* User-provided facts.
* Assumptions.
* Missing evidence.
* Feasibility constraints.
* Trade-offs supporting the recommendation.

Unknown information must not silently become a zero score. If numerical scoring is proposed later, it will require explicit scales, weights and limitations.

Ask up to three decision-critical clarification questions at a time. Skipped answers should remain visible as unknowns or explicit assumptions.

4. CONFIRMED CHOICES

* Interface and documentation: English.
* Working product name: AI Initiative Advisor.
* Offline fixture mode: yes, explicitly labelled as sample data.
* Never silently replace a failed live model call with a fixture response.
* Local execution; no hosting or Docker at this stage.
* Keep the runtime provider decision open until we confirm available API access. This does not block the skeleton.

Keep React/Vite/TypeScript and FastAPI. Justify them through suitability and maintainability. Neither using a component library nor using TypeScript inherently conflicts with IoC.

5. IMPLEMENT ONLY THE SKELETON

After updating the documents, implement:

* The frontend and backend project structure.
* A FastAPI health endpoint.
* A minimal frontend shell showing the proposed layout, clearly identified as an unfinished prototype.
* The documented root startup command: npm run dev.
* An .env.example containing placeholders only.
* Appropriate Git ignore rules.
* Clear first-time setup instructions suitable for Windows.

Do not implement model calls, runtime prompts, scoring, advisory orchestration or the full scenario flow yet.

Verify the startup command, backend health response and frontend-to-backend connection where your environment permits. Report exactly what you checked and what remains unverified.

6. GITHUB REVIEW PREPARATION

Prepare the repository for eventual public review. Include no secrets, employer source code or real operational data. Keep documentation truthful about the project's current stage.

Make separate local commits for the documentation corrections and the skeleton. I will handle publishing the repository to GitHub; do not create a remote or push yet.

Finish with:

* A summary of changes.
* The resulting file structure.
* Setup and startup instructions.
* Checks performed and remaining limitations.
* Local commit identifiers.

Then stop for review.
