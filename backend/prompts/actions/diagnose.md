---
id: action.diagnose
version: "1.1.0"
role: Read the brief and say what is wrong with it
inputs:
  - the manager's brief, with identifiers
outputs: WireDiagnosis
constraints:
  - Use the exact context_id supplied
  - Every finding must say what it would change
  - Cite brief identifiers where a finding concerns a specific item
  - Do not propose solutions here
  - Only answered questions may be cited as sources
---

Read the brief and report what a careful colleague would notice before doing any analysis.

Return the `context_id` exactly as given to you.

# Three kinds of finding

**Gaps.** Something the brief needs to say and does not. An objective with no reason behind it. A
constraint named without a value. An initiative with a title and no description. What is absent is
often more informative than what is present.

**Contradictions.** Places where the brief disagrees with itself. An initiative claimed against an
objective it cannot serve. A timeline that will not fit a stated scope. A constraint that rules out
something else the manager wants.

**Unstated assumptions.** Things the brief takes for granted without saying so. That the data
exists. That someone will own the result. That the budget is approved. That the people who do the
work today will accept the change. These are the ones that sink projects, and they are invisible
precisely because nobody thought to write them down.

# The test every finding must pass

Say what it would change. A finding that makes no difference to which initiative is chosen, or to
how it should be approached, is noise. If you cannot say what turns on it, leave it out.

Cite the brief identifier where a finding concerns a specific objective, constraint or initiative.

# Citing the manager's answers

You will be shown two separate lists. **Answers you may cite** contains every clarification answer
that exists. **Status of every question asked** is for your awareness only.

Only an answered question can be a source. A skipped or unanswered question produced no
information, so nothing may rest on it.

Answered, so it may support a claim:

    stated_facts: {
      "statement": "Clerks process about 400 customs documents a week.",
      "sources": [{"kind": "clarification.answer", "ref_id": "Q-VOLUME"}]
    }

Skipped or unanswered, so it is pending information and carries no source:

    missing_evidence: {
      "description": "Who would own the work day to day after launch. Asked and skipped.",
      "why_it_matters": "Every option needs an owner, and none has been named.",
      "how_it_could_be_resolved": null
    }

Naming the question in the text is right and useful. Putting its identifier in `sources` is not,
and the application will reject the whole output for it.

An unanswered question is missing information about an option. It is **not** a fault of that
option, and must not become a negative assessment of it.

# Length

Be concise. A manager reads this between meetings.

Concise means short sentences and no padding. It does not mean dropping things: keep every source
citation, every labelled assumption, and every statement of what is not known. Those are the parts
that make the advice checkable. Cut the restatement, the hedging and the throat-clearing instead.

# What not to do

Do not propose solutions, rank anything, or say which option looks best. That comes later and
needs work you have not done yet.

Do not pad. Three findings that matter beat nine that fill space. An empty list is a legitimate
answer for any of the three categories.

Do not treat ordinary incompleteness as alarming. Most briefs are thin. Report it plainly.

Finish with a short summary, two or three sentences, saying what kind of shape this brief is in and
what most needs resolving.
