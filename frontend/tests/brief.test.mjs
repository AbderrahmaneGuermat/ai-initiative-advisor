// Draft editing of the brief, and when the advice on screen stops applying.
//
// These are the guarantees the editor relies on: a cancelled draft never
// touches the brief, an unchanged draft changes nothing, and advice is
// withdrawn exactly when the brief no longer matches the session's.

import assert from "node:assert/strict";
import { test } from "node:test";

import { applyDraft, briefDiffersFromSession, draftOf, sameBrief } from "../src/brief.ts";

const sessionBrief = {
  organisation: "Example Ltd",
  situation: "A regional operator.",
  objectives: [{ id: "OBJ-LATE", statement: "Reduce late deliveries", rationale: "Customers." }],
  constraints: [{ id: "CON-TEAM", kind: "headcount", value: "0.7 FTE over three months" }],
  initiatives: [{ id: "INI-DOCS", name: "Customs document extraction", description: null }],
};

test("a draft is a copy: editing it leaves the brief untouched (cancel is free)", () => {
  const brief = draftOf(sessionBrief);
  const draft = draftOf(brief);
  draft.constraints[0].value = "A much longer staffing description that is then abandoned.";
  draft.objectives.push({ id: "OBJ-NEW", statement: "Something else", rationale: null });
  assert.equal(brief.constraints[0].value, "0.7 FTE over three months");
  assert.equal(brief.objectives.length, 1);
  assert.equal(briefDiffersFromSession(sessionBrief, brief), false);
});

test("applying an unchanged draft returns the same brief and keeps advice current", () => {
  const brief = draftOf(sessionBrief);
  const applied = applyDraft(brief, draftOf(brief));
  assert.equal(applied, brief);
  assert.equal(briefDiffersFromSession(sessionBrief, applied), false);
});

test("an edit that is typed and then undone by hand counts as unchanged", () => {
  const brief = draftOf(sessionBrief);
  const draft = draftOf(brief);
  draft.situation = "Something different.";
  draft.situation = "A regional operator.";
  assert.equal(applyDraft(brief, draft), brief);
});

test("applying a changed draft replaces the brief and withdraws the advice", () => {
  const brief = draftOf(sessionBrief);
  const draft = draftOf(brief);
  draft.constraints[0].value = "1.0 FTE";
  const applied = applyDraft(brief, draft);
  assert.notEqual(applied, brief);
  assert.equal(applied.constraints[0].value, "1.0 FTE");
  assert.equal(briefDiffersFromSession(sessionBrief, applied), true);
});

test("discarding the changes, by restoring the session brief, makes the advice current again", () => {
  assert.equal(briefDiffersFromSession(sessionBrief, draftOf(sessionBrief)), false);
});

test("key order never makes two identical briefs differ", () => {
  const reordered = {
    initiatives: sessionBrief.initiatives,
    constraints: sessionBrief.constraints,
    objectives: sessionBrief.objectives.map((o) => ({ rationale: o.rationale, statement: o.statement, id: o.id })),
    situation: sessionBrief.situation,
    organisation: sessionBrief.organisation,
  };
  assert.equal(sameBrief(sessionBrief, reordered), true);
});

test("an empty optional field and a cleared one are the same; a value is not", () => {
  const cleared = draftOf(sessionBrief);
  cleared.initiatives[0].description = null;
  assert.equal(sameBrief(sessionBrief, cleared), true);
  cleared.initiatives[0].description = "Now described.";
  assert.equal(sameBrief(sessionBrief, cleared), false);
});

test("without a session nothing is withdrawn", () => {
  assert.equal(briefDiffersFromSession(null, draftOf(sessionBrief)), false);
  assert.equal(briefDiffersFromSession(undefined, draftOf(sessionBrief)), false);
});
