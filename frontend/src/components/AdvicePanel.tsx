import Placeholder from "./Placeholder";

/**
 * Right region: the current standing advice.
 *
 * Kept on screen permanently so the manager can see the answer and its basis
 * at the same time. After a revision it shows what changed rather than
 * silently replacing itself, because a manager who cannot see what moved has
 * no reason to trust the second answer.
 *
 * Skeleton stage: structure only.
 */
export default function AdvicePanel() {
  return (
    <section className="panel panel--advice" aria-labelledby="advice-heading">
      <div className="panel__header">
        <h2 id="advice-heading" className="panel__title">
          Current advice
        </h2>
        <p className="panel__hint">The standing recommendation and what it rests on</p>
      </div>

      <div className="panel__body">
        <Placeholder label="Shortlist" note="Preferred initiatives, in order of priority" />
        <Placeholder
          label="Basis"
          note="Which stated facts and which labelled assumptions support the choice"
        />
        <Placeholder label="Risks" note="What could make this the wrong call" />
        <Placeholder
          label="Change log"
          note="What moved and what held after the last revision"
        />
        <Placeholder label="Export" note="Decision brief as Markdown or JSON" />
      </div>
    </section>
  );
}
