import { useId, useState } from "react";

import type { Brief, Constraint } from "../api/client";
import AutoTextarea from "./AutoTextarea";
import { CalendarIcon, EditIcon, PeopleIcon, ShieldIcon, TargetIcon, WalletIcon } from "./icons";

/**
 * The context sidebar: who is being advised, and under what limits.
 *
 * A compact read-only summary by default, with the whole brief editable behind
 * one clearly labelled control. The summary shows the values the brief
 * actually holds; nothing is parsed out of prose to fill a slot, and a
 * constraint the manager left empty says "Not stated" rather than being hidden.
 *
 * Long constraint text is shown in full and wraps. It is not truncated, because
 * a constraint the manager cannot read is a constraint they cannot check.
 *
 * The start control sits directly under the organisation so that it is reachable
 * without scrolling on a 1366 × 768 screen.
 */

const ICONS: Record<string, (p: { size?: number }) => JSX.Element> = {
  budget: WalletIcon,
  headcount: PeopleIcon,
  timeline: CalendarIcon,
  regulatory: ShieldIcon,
};

function constraintIcon(kind: string) {
  const key = kind.trim().toLowerCase();
  return ICONS[key] ?? ShieldIcon;
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
  const editorId = useId();

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
      <section className="side-block">
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
      </section>

      <section className="side-block">
        <h2 className="side-label">What matters</h2>
        {brief.objectives.length === 0 ? (
          <p className="side-empty">No objectives stated.</p>
        ) : (
          <ul className="side-list">
            {brief.objectives.map((objective) => (
              <li key={objective.id} className="side-item">
                <span className="side-item__icon" aria-hidden="true">
                  <TargetIcon size={14} />
                </span>
                <span className="side-item__body">
                  <span className="side-item__text">{objective.statement}</span>
                  {objective.rationale && (
                    <span className="side-item__sub">{objective.rationale}</span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="side-block">
        <h2 className="side-label">Within these limits</h2>
        {brief.constraints.length === 0 ? (
          <p className="side-empty">No constraints stated.</p>
        ) : (
          <ul className="side-list">
            {brief.constraints.map((constraint: Constraint) => {
              const Icon = constraintIcon(constraint.kind);
              return (
                <li key={constraint.id} className="side-item">
                  <span className="side-item__icon" aria-hidden="true">
                    <Icon size={14} />
                  </span>
                  <span className="side-item__body">
                    <span className="side-item__kind">{constraint.kind}</span>
                    {constraint.value ? (
                      <span className="side-item__text side-item__text--clamp" title={constraint.value}>
                        {constraint.value}
                      </span>
                    ) : (
                      <span className="side-item__text side-item__text--empty">Not stated</span>
                    )}
                  </span>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <section className="side-block">
        <h2 className="side-label">Options considered</h2>
        <ul className="side-list side-list--plain">
          {brief.initiatives.map((initiative) => (
            <li key={initiative.id} className="side-item side-item--tight">
              <span className="side-item__body">
                <span className="side-item__text">{initiative.name}</span>
                {!initiative.description && (
                  <span className="side-item__sub side-item__sub--warn">Not described</span>
                )}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <button
        type="button"
        className="button button--quiet button--block"
        aria-expanded={editing}
        aria-controls={editorId}
        onClick={() => setEditing((v) => !v)}
      >
        <EditIcon size={14} />
        {editing ? "Hide the full brief" : "Review or edit the full brief"}
      </button>

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
    </aside>
  );
}
