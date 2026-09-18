import Placeholder from "./Placeholder";

/**
 * Left region: the manager's situation.
 *
 * Objectives, constraints and candidate initiatives stay permanently visible
 * here, because editing a constraint is the primary interaction of the
 * product rather than a setting buried in a dialog. Revision is triggered from
 * this panel once the advisory loop exists.
 *
 * Skeleton stage: structure only. No inputs are wired up.
 */
export default function ContextPanel() {
  return (
    <section className="panel panel--context" aria-labelledby="context-heading">
      <div className="panel__header">
        <h2 id="context-heading" className="panel__title">
          Context
        </h2>
        <p className="panel__hint">What the advisor knows about your situation</p>
      </div>

      <div className="panel__body">
        <Placeholder label="Objectives" note="What the manager is trying to achieve" />
        <Placeholder
          label="Constraints"
          note="Budget, timeline, headcount, risk appetite. Editing one of these triggers a revision."
        />
        <Placeholder
          label="Candidate initiatives"
          note="The options under consideration, added by the manager or loaded from a fictional sample scenario"
        />
        <Placeholder
          label="Open unknowns"
          note="Questions left unanswered stay visible here as unknowns or labelled assumptions. They are never dropped."
        />
      </div>
    </section>
  );
}
