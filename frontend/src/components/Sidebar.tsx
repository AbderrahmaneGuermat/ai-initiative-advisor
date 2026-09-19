import { useId, useState } from "react";

import type { Brief, Constraint } from "../api/client";
import ClampText from "./ClampText";
import { ChevronIcon, TargetIcon } from "./icons";

/**
 * The context sidebar: who is being advised, and under what limits.
 *
 * The session controls come first: start, and the full brief behind one
 * clearly labelled control directly beneath it. The editor itself opens in the
 * main column, where long text has room; this column stays a summary.
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
  onStart,
  onEdit,
  editing,
  editorId,
  busy,
  sessionActive,
  briefEdited,
  emptyNote,
}: {
  brief: Brief | null;
  onStart: () => void;
  /** Open or close the brief editor in the main column. */
  onEdit: () => void;
  editing: boolean;
  editorId: string;
  busy: boolean;
  sessionActive: boolean;
  /** True when the brief on screen is not the one the session was run on. */
  briefEdited: boolean;
  /** What to say while there is no brief: loading, or nothing to load. */
  emptyNote: string;
}) {
  const [contextOpen, setContextOpen] = useState(false);
  const contextId = useId();

  if (!brief) {
    return (
      <aside className="sidebar" aria-label="Context">
        <p className="muted">{emptyNote}</p>
      </aside>
    );
  }

  const startLabel = sessionActive ? "Start again" : "Start advisory session";

  return (
    <aside className="sidebar" aria-label="Context">
      <section className="side-top">
        <h2 className="side-label">Your organisation</h2>
        <p className="side-org">{brief.organisation}</p>

        {/* Once a session exists, starting again is available but secondary:
            the advice and its first actions are what the page is for. When
            the brief has changed, the main column owns the one "start"
            action, so it is not repeated here. */}
        {!(sessionActive && briefEdited) && (
          <button
            className={
              sessionActive ? "button button--block" : "button button--primary button--block"
            }
            onClick={onStart}
            disabled={busy || editing}
          >
            {busy ? "Working…" : startLabel}
          </button>
        )}

        <div className="side-controls">
          <button
            type="button"
            className="side-link"
            aria-expanded={editing}
            aria-controls={editing ? editorId : undefined}
            onClick={onEdit}
          >
            {editing ? "Close the brief editor" : "Review or edit the full brief"}
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
