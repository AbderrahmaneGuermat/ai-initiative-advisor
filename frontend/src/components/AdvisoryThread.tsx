import Placeholder from "./Placeholder";

/**
 * Centre region: the advisory conversation.
 *
 * A thread of advisory turns rather than a chat log, so the reasoning stays
 * reviewable in order instead of scrolling away. Which turn happens next is
 * decided by a prompt, not by a fixed sequence in code, so this region has no
 * predetermined shape.
 *
 * Skeleton stage: structure only. Nothing is generated.
 */
export default function AdvisoryThread() {
  return (
    <section className="panel panel--thread" aria-labelledby="thread-heading">
      <div className="panel__header">
        <h2 id="thread-heading" className="panel__title">
          Advisory thread
        </h2>
        <p className="panel__hint">
          Diagnosis, clarification, comparison, recommendation and revision, in whatever order the
          situation calls for
        </p>
      </div>

      <div className="panel__body">
        <Placeholder
          label="Diagnosis"
          note="Gaps, contradictions and unstated assumptions found in the brief"
        />
        <Placeholder
          label="Clarification"
          note="At most three decision-critical questions at a time. Answering is optional; skipping is recorded."
        />
        <Placeholder
          label="Comparison"
          note="Each option set out as stated facts, assumptions, missing evidence, feasibility constraints and trade-offs. No numerical scoring."
        />
        <Placeholder
          label="Recommendation"
          note="A justified choice traceable to the facts and the labelled assumptions, with risks and first moves"
        />
        <Placeholder
          label="Revision"
          note="After a constraint changes: what moved, what held, and why"
        />
      </div>
    </section>
  );
}
