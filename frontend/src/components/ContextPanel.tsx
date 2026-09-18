import type { Brief } from "../api/client";

/**
 * Left region: the manager's situation, editable.
 *
 * Constraints stay visible and editable because changing one is the product's
 * primary interaction. In this iteration a change starts a new session rather
 * than revising the current advice, and the panel says so plainly instead of
 * implying a revision that does not happen.
 *
 * Adding or removing objectives, constraints and initiatives is not implemented
 * yet. Existing entries can be edited.
 */
export default function ContextPanel({
  brief,
  onChange,
  onStart,
  busy,
  sessionActive,
  briefEdited,
}: {
  brief: Brief | null;
  onChange: (brief: Brief) => void;
  onStart: () => void;
  busy: boolean;
  sessionActive: boolean;
  briefEdited: boolean;
}) {
  if (!brief) {
    return (
      <section className="panel panel--context" aria-labelledby="context-heading">
        <div className="panel__header">
          <h2 id="context-heading" className="panel__title">
            Context
          </h2>
        </div>
        <div className="panel__body">
          <p className="muted">Loading the sample scenario…</p>
        </div>
      </section>
    );
  }

  const update = (patch: Partial<Brief>) => onChange({ ...brief, ...patch });

  const startLabel = sessionActive
    ? briefEdited
      ? "Start a new session with these changes"
      : "Start again"
    : "Start advisory session";

  return (
    <section className="panel panel--context" aria-labelledby="context-heading">
      <div className="panel__header">
        <h2 id="context-heading" className="panel__title">
          Context
        </h2>
        <p className="panel__hint">
          Fictional sample scenario. Edit any field before starting.
        </p>
      </div>

      <div className="panel__body">
        <label className="field">
          <span className="field__label">Organisation</span>
          <input
            className="field__input"
            value={brief.organisation}
            onChange={(event) => update({ organisation: event.target.value })}
          />
        </label>

        <label className="field">
          <span className="field__label">Situation</span>
          <textarea
            className="field__input field__input--area"
            rows={4}
            value={brief.situation ?? ""}
            onChange={(event) => update({ situation: event.target.value || null })}
          />
        </label>

        <h3 className="group__title">Objectives</h3>
        {brief.objectives.map((objective, index) => (
          <div className="group" key={objective.id}>
            <label className="field">
              <span className="field__label">Objective {index + 1}</span>
              <input
                className="field__input"
                value={objective.statement}
                onChange={(event) => {
                  const objectives = [...brief.objectives];
                  objectives[index] = { ...objective, statement: event.target.value };
                  update({ objectives });
                }}
              />
            </label>
            <label className="field">
              <span className="field__label field__label--sub">Why it matters</span>
              <input
                className="field__input"
                placeholder="Not stated"
                value={objective.rationale ?? ""}
                onChange={(event) => {
                  const objectives = [...brief.objectives];
                  objectives[index] = { ...objective, rationale: event.target.value || null };
                  update({ objectives });
                }}
              />
            </label>
          </div>
        ))}

        <h3 className="group__title">Constraints</h3>
        {brief.constraints.map((constraint, index) => (
          <label className="field" key={constraint.id}>
            <span className="field__label">{constraint.kind}</span>
            <input
              className="field__input"
              placeholder="Not stated"
              value={constraint.value ?? ""}
              onChange={(event) => {
                const constraints = [...brief.constraints];
                constraints[index] = { ...constraint, value: event.target.value || null };
                update({ constraints });
              }}
            />
          </label>
        ))}

        <h3 className="group__title">Candidate initiatives</h3>
        {brief.initiatives.map((initiative, index) => (
          <div className="group" key={initiative.id}>
            <label className="field">
              <span className="field__label">{initiative.id}</span>
              <input
                className="field__input"
                value={initiative.name}
                onChange={(event) => {
                  const initiatives = [...brief.initiatives];
                  initiatives[index] = { ...initiative, name: event.target.value };
                  update({ initiatives });
                }}
              />
            </label>
            <label className="field">
              <span className="field__label field__label--sub">What it involves</span>
              <textarea
                className="field__input field__input--area"
                rows={2}
                placeholder="Not described"
                value={initiative.description ?? ""}
                onChange={(event) => {
                  const initiatives = [...brief.initiatives];
                  initiatives[index] = { ...initiative, description: event.target.value || null };
                  update({ initiatives });
                }}
              />
            </label>
          </div>
        ))}

        {sessionActive && briefEdited && (
          <p className="notice notice--info">
            You have changed the brief. Starting again creates a new session with fresh advice.
            The current advice is not revised.
          </p>
        )}

        <button className="button button--primary" onClick={onStart} disabled={busy}>
          {busy ? "Working…" : startLabel}
        </button>
      </div>
    </section>
  );
}
