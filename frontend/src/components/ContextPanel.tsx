import type { Brief } from "../api/client";
import AutoTextarea from "./AutoTextarea";

/**
 * Left region: the manager's situation, editable.
 *
 * **The primary action sits at the top.** The walkthrough showed the start
 * button below the entire form, so starting the sample scenario meant
 * scrolling past every field of a brief the manager had not asked to edit.
 * Editing is still available, now behind labelled sections that summarise
 * themselves, so the common case is one click and the uncommon case is one
 * click more.
 *
 * Adding and removing entries is still not implemented; existing ones can be
 * edited.
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

  const unstated =
    brief.objectives.filter((o) => !o.rationale).length +
    brief.constraints.filter((c) => !c.value).length +
    brief.initiatives.filter((i) => !i.description).length;

  return (
    <section className="panel panel--context" aria-labelledby="context-heading">
      <div className="panel__header">
        <h2 id="context-heading" className="panel__title">
          Context
        </h2>
        <p className="panel__hint">Fictional sample scenario. Edit any field before starting.</p>
      </div>

      <div className="panel__body">
        {/* The action first, then the detail. */}
        <div className="start">
          <p className="start__org">{brief.organisation}</p>
          <p className="start__counts">
            {brief.objectives.length} objectives · {brief.constraints.length} constraints ·{" "}
            {brief.initiatives.length} initiatives
            {unstated > 0 && <> · {unstated} fields not stated</>}
          </p>

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

        <details className="section">
          <summary className="section__summary">
            <span className="section__label">Organisation and situation</span>
            <span className="section__hint">Read first</span>
          </summary>
          <div className="section__body">
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
          </div>
        </details>

        <details className="section">
          <summary className="section__summary">
            <span className="section__label">Objectives</span>
            <span className="section__hint">{brief.objectives.length} listed</span>
          </summary>
          <div className="section__body">
            {brief.objectives.map((objective, index) => (
              <div className="group" key={objective.id}>
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
          </div>
        </details>

        <details className="section">
          <summary className="section__summary">
            <span className="section__label">Constraints</span>
            <span className="section__hint">{brief.constraints.length} listed</span>
          </summary>
          <div className="section__body">
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
          </div>
        </details>

        <details className="section">
          <summary className="section__summary">
            <span className="section__label">Candidate initiatives</span>
            <span className="section__hint">{brief.initiatives.length} listed</span>
          </summary>
          <div className="section__body">
            {brief.initiatives.map((initiative, index) => (
              <div className="group" key={initiative.id}>
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
        </details>
      </div>
    </section>
  );
}
