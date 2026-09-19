import { useEffect, useRef, useState } from "react";

import type { Brief } from "../api/client";
import { draftOf, sameBrief } from "../brief";
import AutoTextarea from "./AutoTextarea";

/**
 * The full brief, edited in the main column.
 *
 * **Everything here is a draft.** The editor copies the brief when it opens and
 * changes only that copy. Cancel discards it; nothing reaches the brief, the
 * session or the backend. Apply hands the draft back, and the shell decides
 * what it means: an unchanged draft changes nothing, a changed one means the
 * existing advice no longer describes this brief.
 *
 * Opening, editing, applying and cancelling never start a session and never
 * call the advisor. Starting one stays a separate, deliberate action.
 */
export default function BriefEditor({
  brief,
  sessionActive,
  onApply,
  onCancel,
}: {
  brief: Brief;
  sessionActive: boolean;
  onApply: (draft: Brief) => void;
  onCancel: () => void;
}) {
  const [draft, setDraft] = useState<Brief>(() => draftOf(brief));
  const headingRef = useRef<HTMLHeadingElement>(null);
  const changed = !sameBrief(brief, draft);

  useEffect(() => {
    headingRef.current?.focus();
  }, []);

  const update = (patch: Partial<Brief>) => setDraft((current) => ({ ...current, ...patch }));

  return (
    <section className="brief-editor" aria-labelledby="brief-editor-heading">
      <p className="eyebrow">Your decision brief</p>
      <h1 className="h1" id="brief-editor-heading" tabIndex={-1} ref={headingRef}>
        Edit your brief
      </h1>
      <p className="lede">
        {sessionActive
          ? "The current advice was produced for the brief as it stands. If you apply a change, that advice no longer describes your brief and a new advisory session is needed. Nothing starts until you choose to start it."
          : "Changes here are used when you start the advisory session. Nothing runs until you do."}
      </p>

      <div className="brief-editor__section">
        <h2 className="brief-editor__heading">Organisation</h2>
        <label className="field">
          <span className="field__label">Name</span>
          <AutoTextarea
            value={draft.organisation}
            onChange={(value) => update({ organisation: value })}
          />
        </label>
        <label className="field">
          <span className="field__label">Situation</span>
          <AutoTextarea
            value={draft.situation ?? ""}
            minRows={3}
            placeholder="Not stated"
            onChange={(value) => update({ situation: value || null })}
          />
        </label>
      </div>

      <div className="brief-editor__section">
        <h2 className="brief-editor__heading">Objectives</h2>
        {draft.objectives.map((objective, index) => (
          <fieldset className="brief-editor__group" key={objective.id}>
            <legend className="brief-editor__legend">
              Objective {index + 1} <code>{objective.id}</code>
            </legend>
            <label className="field">
              <span className="field__label">What you want to achieve</span>
              <AutoTextarea
                value={objective.statement}
                onChange={(value) => {
                  const objectives = [...draft.objectives];
                  objectives[index] = { ...objective, statement: value };
                  update({ objectives });
                }}
              />
            </label>
            <label className="field">
              <span className="field__label">Why it matters</span>
              <AutoTextarea
                value={objective.rationale ?? ""}
                minRows={2}
                placeholder="Not stated"
                onChange={(value) => {
                  const objectives = [...draft.objectives];
                  objectives[index] = { ...objective, rationale: value || null };
                  update({ objectives });
                }}
              />
            </label>
          </fieldset>
        ))}
      </div>

      <div className="brief-editor__section">
        <h2 className="brief-editor__heading">Constraints</h2>
        {draft.constraints.map((constraint, index) => (
          <label className="field" key={constraint.id}>
            <span className="field__label">
              {constraint.kind} <code>{constraint.id}</code>
            </span>
            <AutoTextarea
              value={constraint.value ?? ""}
              minRows={2}
              placeholder="Not stated"
              onChange={(value) => {
                const constraints = [...draft.constraints];
                constraints[index] = { ...constraint, value: value || null };
                update({ constraints });
              }}
            />
          </label>
        ))}
      </div>

      <div className="brief-editor__section">
        <h2 className="brief-editor__heading">Candidate initiatives</h2>
        {draft.initiatives.map((initiative, index) => (
          <fieldset className="brief-editor__group" key={initiative.id}>
            <legend className="brief-editor__legend">
              Initiative {index + 1} <code>{initiative.id}</code>
            </legend>
            <label className="field">
              <span className="field__label">Name</span>
              <AutoTextarea
                value={initiative.name}
                onChange={(value) => {
                  const initiatives = [...draft.initiatives];
                  initiatives[index] = { ...initiative, name: value };
                  update({ initiatives });
                }}
              />
            </label>
            <label className="field">
              <span className="field__label">What it involves</span>
              <AutoTextarea
                value={initiative.description ?? ""}
                minRows={2}
                placeholder="Not described"
                onChange={(value) => {
                  const initiatives = [...draft.initiatives];
                  initiatives[index] = { ...initiative, description: value || null };
                  update({ initiatives });
                }}
              />
            </label>
          </fieldset>
        ))}
      </div>

      <div className="brief-editor__bar">
        <span className="brief-editor__state" aria-live="polite">
          {changed ? "You have changes that are not applied yet." : "No changes yet."}
        </span>
        <div className="brief-editor__actions">
          <button type="button" className="button" onClick={onCancel}>
            Cancel and return
          </button>
          <button type="button" className="button button--primary" onClick={() => onApply(draft)}>
            Apply changes
          </button>
        </div>
      </div>
    </section>
  );
}
