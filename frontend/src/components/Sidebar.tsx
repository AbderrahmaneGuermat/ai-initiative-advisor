import { useId, useState } from "react";

import type { Brief, Constraint } from "../api/client";
import AutoTextarea from "./AutoTextarea";
import ClampText from "./ClampText";
import { ChevronIcon, EditIcon, TargetIcon } from "./icons";

/**
 * The context sidebar: who is being advised, and under what limits.
 *
 * The session controls come first: start, and the full brief behind one
 * clearly labelled control directly beneath it. The editor opens there, next to
 * the button it affects, rather than below everything else.
 *
 * The compact view summarises. Objectives show their titles; why each matters
 * is in the full brief. Constraints show their real kind and their full value.
 * Nothing is parsed out of prose to make a shorter label, and a long value is
 * cut to a few lines with a "Show all" button, never only a tooltip.
 *
 * On a narrow screen the context folds behind its own disclosure, so the work
 * in the main column is reached without scrolling past it.
 */

function kindLabel(kind: string): string {
  const k = kind.trim();
  return k ? k.charAt(0).toUpperCase() + k.slice(1) : "Constraint";
}

export default function Sidebar({
  brief,
  onChange,
  onStart,
  busy,
  sessionActive,
  briefEdited,
  emptyNote,
}: {
  brief: Brief | null;
  onChange: (brief: Brief) => void;
  onStart: () => void;
  busy: boolean;
  sessionActive: boolean;
  briefEdited: boolean;
  /** What to say while there is no brief: loading, or nothing to load. */
  emptyNote: string;
}) {
  const [editing, setEditing] = useState(false);
  const [contextOpen, setContextOpen] = useState(false);
  const editorId = useId();
  const contextId = useId();

  if (!brief) {
    return (
      <aside className="sidebar" aria-label="Context">
        <p className="muted">{emptyNote}</p>
      </aside>
    );
  }

  const update = (patch: Partial<Brief>) => onChange({ ...brief, ...patch });

  const startLabel = sessionActive
    ? briefEdited
      ? "Start a new session"
      : "Start again"
    : "Start advisory session";

  return (
    <aside className="sidebar" aria-label="Context">
      <section className="side-top">
        <h2 className="side-label">Your organisation</h2>
        <p className="side-org">{brief.organisation}</p>

        {briefEdited && sessionActive && (
          <p className="side-note side-note--warn">
            The brief has changed. Starting again creates a new session. The current advice is not
            revised.
          </p>
        )}

        <button className="button button--primary button--block" onClick={onStart} disabled={busy}>
          {busy ? "Working…" : startLabel}
        </button>

        <div className="side-controls">
          <button
            type="button"
            className="side-link"
            aria-expanded={editing}
            aria-controls={editorId}
            onClick={() => setEditing((v) => !v)}
          >
            <EditIcon size={13} />
            {editing ? "Hide the full brief" : "Review or edit the full brief"}
          </button>

          <button
            type="button"
            className="side-link side-link--context"
            aria-expanded={contextOpen}
            aria-controls={contextId}
            onClick={() => setContextOpen((v) => !v)}
          >
            <ChevronIcon size={13} className={contextOpen ? "rot90" : ""} />
            {contextOpen ? "Hide context" : "Show context"}
          </button>
        </div>
      </section>

      {editing && (
        <div className="editor" id={editorId}>
          <label className="field">
            <span className="field__label">Organisation</span>
            <AutoTextarea
              value={brief.organisation}
              onChange={(value) => update({ organisation: value })}
            />
          </label>

          <label className="field">
            <span className="field__label">Situation</span>
            <AutoTextarea
              value={brief.situation ?? ""}
              minRows={3}
              placeholder="Not stated"
              onChange={(value) => update({ situation: value || null })}
            />
          </label>

          <h3 className="editor__heading">Objectives</h3>
          {brief.objectives.map((objective, index) => (
            <div className="editor__group" key={objective.id}>
              <label className="field">
                <span className="field__label">Objective {index + 1}</span>
                <AutoTextarea
                  value={objective.statement}
                  onChange={(value) => {
                    const objectives = [...brief.objectives];
                    objectives[index] = { ...objective, statement: value };
                    update({ objectives });
                  }}
                />
              </label>
              <label className="field">
                <span className="field__label field__label--sub">Why it matters</span>
                <AutoTextarea
                  value={objective.rationale ?? ""}
                  placeholder="Not stated"
                  onChange={(value) => {
                    const objectives = [...brief.objectives];
                    objectives[index] = { ...objective, rationale: value || null };
                    update({ objectives });
                  }}
                />
              </label>
            </div>
          ))}

          <h3 className="editor__heading">Constraints</h3>
          {brief.constraints.map((constraint, index) => (
            <label className="field" key={constraint.id}>
              <span className="field__label">{constraint.kind}</span>
              <AutoTextarea
                value={constraint.value ?? ""}
                placeholder="Not stated"
                onChange={(value) => {
                  const constraints = [...brief.constraints];
                  constraints[index] = { ...constraint, value: value || null };
                  update({ constraints });
                }}
              />
            </label>
          ))}

          <h3 className="editor__heading">Candidate initiatives</h3>
          {brief.initiatives.map((initiative, index) => (
            <div className="editor__group" key={initiative.id}>
              <label className="field">
                <span className="field__label">{initiative.id}</span>
                <AutoTextarea
                  value={initiative.name}
                  onChange={(value) => {
                    const initiatives = [...brief.initiatives];
                    initiatives[index] = { ...initiative, name: value };
                    update({ initiatives });
                  }}
                />
              </label>
              <label className="field">
                <span className="field__label field__label--sub">What it involves</span>
                <AutoTextarea
                  value={initiative.description ?? ""}
                  minRows={2}
                  placeholder="Not described"
                  onChange={(value) => {
                    const initiatives = [...brief.initiatives];
                    initiatives[index] = { ...initiative, description: value || null };
                    update({ initiatives });
                  }}
                />
              </label>
            </div>
          ))}
        </div>
      )}

      <div className={contextOpen ? "side-context is-open" : "side-context"} id={contextId}>
        <section className="side-block">
          <h2 className="side-heading">What matters</h2>
          {brief.objectives.length === 0 ? (
            <p className="side-empty">No objectives stated.</p>
          ) : (
            <ul className="side-goals">
              {brief.objectives.map((objective) => (
                <li key={objective.id}>
                  <TargetIcon size={13} />
                  <span>{objective.statement}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="side-block">
          <h2 className="side-heading">Within these limits</h2>
          {brief.constraints.length === 0 ? (
            <p className="side-empty">No constraints stated.</p>
          ) : (
            <dl className="side-rows">
              {brief.constraints.map((constraint: Constraint) => (
                <div className="side-row" key={constraint.id}>
                  <dt className="side-row__label">{kindLabel(constraint.kind)}</dt>
                  <dd className="side-row__value">
                    {constraint.value ? (
                      <ClampText lines={3}>{constraint.value}</ClampText>
                    ) : (
                      <span className="side-row__empty">Not stated</span>
                    )}
                  </dd>
                </div>
              ))}
            </dl>
          )}
        </section>

        <section className="side-block">
          <h2 className="side-heading">Options considered</h2>
          <ul className="side-options">
            {brief.initiatives.map((initiative) => (
              <li key={initiative.id}>
                {initiative.name}
                {!initiative.description && <span className="side-options__warn">Not described</span>}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </aside>
  );
}
