# Prompt 001 — Project Brief

- **Date received:** 2026-09-18
- **Author:** Project owner (assessment candidate)
- **Assistant acting on it:** Claude (Claude Code)
- **Outcome recorded in:** [../worklog.md](../worklog.md)

The text below is the instruction exactly as received.

---

You are my development collaborator for a BlueCallom Enterprise AI Application Developer assessment.

We will work incrementally. Your first task is to organise the repository, document the requirements and propose an implementation plan. Do not implement the application yet.

PROJECT CONTEXT

The assessment asks me to:

1. Build a simple strategy-consulting application for managers with AI assistance, following BlueCallom's Intelligence-over-Code (IoC) method.
2. Explain the prompts used to develop it.
3. Design a sample enterprise AI interface and explain the UI/UX decisions.

We will address the application and UI requirements through the same project.

Our proposed application helps managers prioritise enterprise AI initiatives based on their objectives, resources and constraints. It should ask relevant clarification questions, compare alternatives, provide a justified recommendation and revise its advice when constraints change.

Review the official method before proposing the architecture:
https://bluecallom.com/intelligence-over-code-method/

Distinguish requirements stated by BlueCallom from our own implementation choices.

REPOSITORY AND DEVELOPMENT RECORD

If the working directory is not already a Git repository, initialise one. Preserve existing files and work.

Create:

* README.md: purpose, current status and planned local execution.
* docs/requirements.md: assessment requirements, proposed scope and open decisions.
* docs/architecture.md: proposed architecture and responsibilities.
* docs/decisions.md: technical and product decisions, with their rationale.
* docs/prompts/: the chronological development prompt record.
* docs/worklog.md: work completed, checks performed and unresolved issues.

Save this entire message verbatim as:
docs/prompts/001-project-brief.md

For each subsequent development instruction I send:

* Save its exact text in the next numbered Markdown file before acting.
* Preserve previous entries.
* Record the actual outcome in the worklog, referencing that prompt.
* Never invent prompts, iterations, test results or historical conversations.

Keep development prompts separate from the runtime prompts used by the application.

Record AI assistance accurately: ChatGPT supported requirements analysis and development-prompt preparation; Claude supports implementation. Do not imply that I manually authored every generated line.

DESIGN AND DELIVERY DIRECTION

Propose React for the interface and Python/FastAPI for the backend, explaining any alternative you recommend.

Prompts should direct diagnosis, clarification, comparison and revision. Conventional code should support model communication, state management, validation, calculations and exports where needed.

Plan a GitHub-ready project that runs locally. Hosting and Docker are outside the initial scope. Aim for a simple, documented startup command after first-time setup.

Explain required dependencies and model credentials. Provide an .env.example when implementation begins, and keep secrets out of Git.

Use fictional demonstration data. Do not assume access to BlueCallom's platform or to my employer's systems.

FIRST RESPONSE

After creating the documentation, show me:

* Your understanding of the assessment and IoC.
* The proposed user journey and interface layout.
* The minimum viable scope.
* The architecture and local startup approach.
* The implementation steps and decisions that need my input.

Stop there so we can review the design before implementation.
