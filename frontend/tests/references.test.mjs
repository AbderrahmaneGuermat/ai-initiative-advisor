// Readable references in model prose.
//
// Run with `npm test` (Node's built-in runner; Node 22.6+ strips the types
// from lookup.ts). The property that matters most: rendering never changes
// what the model wrote. Joining the segments back reproduces the text exactly.

import assert from "node:assert/strict";
import { test } from "node:test";

import { opening, referenceIndex, splitReferences } from "../src/lookup.ts";

const session = {
  brief: {
    organisation: "Example Ltd",
    objectives: [{ id: "OBJ-LATE", statement: "Reduce late deliveries", rationale: null }],
    constraints: [{ id: "CON-BUDGET", kind: "budget", value: "about 150,000 EUR" }],
    initiatives: [{ id: "INI-DOCS", name: "Customs document extraction", description: null }],
  },
  questions: [
    { id: "Q-HISTDATA", question: "What data exists?", status: "answered" },
    { id: "Q-BUDGET", question: "Is the budget confirmed?", status: "skipped" },
    { id: "Q-CONTRACT", question: "Can we hire a contractor?", status: "unanswered" },
  ],
};

const index = referenceIndex(session);
const rejoin = (segments) =>
  segments.map((s) => ("text" in s ? s.text : s.ref.id)).join("");

test("known identifiers in prose become readable labels", () => {
  const segments = splitReferences("PDFs in-house (Q-HISTDATA) map to OBJ-LATE.", index);
  const refs = segments.filter((s) => "ref" in s).map((s) => s.ref.label);
  assert.deepEqual(refs, ["your answer", "Reduce late deliveries"]);
});

test("the original text is recoverable exactly", () => {
  const text = "Confirm CON-BUDGET for INI-DOCS; see Q-BUDGET and Q-CONTRACT (INI-DOCS).";
  assert.equal(rejoin(splitReferences(text, index)), text);
});

test("unresolved or look-alike tokens are left as written", () => {
  const text = "Context CTX-LARKFIELD-1, INI-ROUTE and GDPR-EU stay as they are.";
  const segments = splitReferences(text, index);
  assert.equal(segments.length, 1);
  assert.equal(segments[0].text, text);
});

test("partial matches inside longer identifiers are not replaced", () => {
  const text = "INI-DOCS-2 is a different identifier from INI-DOCS.";
  const segments = splitReferences(text, index);
  const ids = segments.filter((s) => "ref" in s).map((s) => s.ref.id);
  assert.deepEqual(ids, ["INI-DOCS"]);
  assert.equal(rejoin(segments), text);
});

test("an answered question reads as the answer; an open one by its own words", () => {
  assert.equal(index.get("Q-HISTDATA").label, "your answer");
  assert.equal(index.get("Q-BUDGET").label, "“Is the budget confirmed?”");
  assert.equal(index.get("Q-CONTRACT").detail, "Can we hire a contractor?");
  assert.equal(index.get("CON-BUDGET").label, "budget constraint");
});

test("a long question is cut to its opening words and marked as cut", () => {
  assert.equal(opening("one two three four five six seven eight"), "one two three four five six…");
  assert.equal(opening("short question?"), "short question?");
});

test("no session means no replacements", () => {
  const text = "OBJ-LATE stays.";
  assert.deepEqual(splitReferences(text, referenceIndex(null)), [{ text }]);
});
