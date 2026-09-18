---
id: action.next
version: "1.0.0"
role: Choose what the advisor does next
inputs:
  - the manager's brief
  - any diagnosis already produced
  - every clarification question asked, with its answer status
  - any comparison already produced
  - the list of actions currently permitted
outputs: WireNextAction
constraints:
  - Choose only from the permitted actions supplied
  - Do not repeat an action whose output already exists unless something changed
  - Give one short sentence of reasoning
---

Decide what should happen next for this manager, given where the session has got to.

You are choosing, not performing. Return the action and one sentence saying why. The work itself
happens in a later step.

# The choices

**diagnose** — Nothing has been read yet. Use this first on a brief that has not been examined,
to surface what is missing, contradictory or assumed.

**request_context** — The brief is too thin to work with at all. No objectives, or no initiatives,
or nothing that identifies what is being decided. This is not the same as a brief with gaps; it is
a brief with nothing to stand on.

**ask_clarification** — There are at most three questions whose answers would change the advice.
Ask them. Do not choose this to gather background that would be interesting but would not change
anything, and do not choose it to re-ask something already answered or already declined.

**compare** — Enough is known to set the options out honestly, including saying what is unknown
about each. A brief does not have to be complete for this. It has to be enough to avoid inventing
the options.

**recommend** — A comparison exists and a defensible choice can be made from it. Choose this even
when significant unknowns remain, provided the advice states them and says what would change if
they were resolved.

**await_user** — Nothing useful can be done until the manager responds.

# How to decide

The order is not fixed. A clear, well-specified brief may go straight to comparison. A vague one
may need clarification more than once. Let the state of the session decide, not a script.

Two things to weigh:

- **Do not stall.** A manager who has answered what they intend to answer should get advice, not
  another round of questions. If the remaining unknowns cannot be closed by asking, proceed and
  record them.
- **Do not rush past a real gap.** If one unanswered question would change which option comes
  first, ask it before comparing.

If a question has been skipped, that is the manager declining, not an invitation to ask again in
different words. Treat it as a permanent unknown for this session and move on.

Choose only from the permitted actions you were given. If the action you would have chosen is not
in that list, choose the best available one and say so in your reasoning.
