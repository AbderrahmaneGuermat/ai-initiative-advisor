import type { SessionView, Stance } from "../api/client";

const STANCE_LABEL: Record<Stance, string> = {
  recommended: "Recommended",
  consider_later: "Consider later",
  not_recommended: "Not recommended",
  insufficient_information: "Not enough information",
};

/**
 * Right region: the standing advice.
 *
 * Open questions are rendered from session state, never from the
 * recommendation's own summary. If the advisor forgets to mention something the
 * manager skipped, it still appears here, because the backend reports it from
 * what actually happened rather than from what the advice says happened.
 */
export default function AdvicePanel({ session }: { session: SessionView | null }) {
  const recommendation = session?.recommendation ?? null;
  const outdated = session?.previous_recommendation ?? null;
  const openQuestions = session?.questions.filter((q) => q.status !== "answered") ?? [];
  const shown = recommendation ?? outdated;
  const isOutdated = recommendation === null && outdated !== null;

  return (
    <section className="panel panel--advice" aria-labelledby="advice-heading">
      <div className="panel__header">
        <h2 id="advice-heading" className="panel__title">
          Current advice
        </h2>
        <p className="panel__hint">The recommendation and what it rests on</p>
      </div>

      <div className="panel__body">
        {!shown && (
          <p className="muted">
            No recommendation yet. It appears once the advisor has compared the options.
          </p>
        )}

        {isOutdated && (
          <div className="notice notice--stale" role="status">
            <strong>Out of date.</strong> You have answered something since this advice was
            written, so it no longer reflects what the advisor knows. It is kept below for
            reference and is not the current recommendation. Select <em>Continue</em> to
            refresh it.
          </div>
        )}

        {shown && (
          <>
            <p className={isOutdated ? "advice__summary advice__summary--stale" : "advice__summary"}>
              {shown.summary}
            </p>

            <ol className={isOutdated ? "shortlist shortlist--stale" : "shortlist"}>
              {shown.items.map((item) => {
                const initiative = session?.brief.initiatives.find(
                  (i) => i.id === item.initiative_id,
                );
                return (
                  <li className="shortlist__item" key={item.initiative_id}>
                    <div className="shortlist__head">
                      <strong>{initiative?.name ?? item.initiative_id}</strong>
                      <span className={`tag tag--${item.stance}`}>
                        {STANCE_LABEL[item.stance]}
                      </span>
                    </div>
                    <p className="shortlist__why">{item.rationale}</p>
                    {item.rests_on_assumptions.length > 0 && (
                      <div className="claims">
                        <span className="claims__label">Rests on</span>
                        <ul className="list">
                          {item.rests_on_assumptions.map((assumption, index) => (
                            <li key={index}>{assumption}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </li>
                );
              })}
            </ol>

            {shown.first_actions.length > 0 && (
              <div className="block">
                <h3 className="block__title">First actions</h3>
                <ol className="list">
                  {shown.first_actions.map((action, index) => (
                    <li key={index}>
                      {action.action} <em>{action.purpose}</em>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {shown.risks.length > 0 && (
              <div className="block">
                <h3 className="block__title">Risks</h3>
                <ul className="list">
                  {shown.risks.map((risk, index) => (
                    <li key={index}>
                      {risk.description} <em>{risk.consequence_if_realised}</em>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="block">
              <h3 className="block__title">How far to trust this</h3>
              <p>{shown.confidence_note}</p>
            </div>
          </>
        )}

        {session && openQuestions.length > 0 && (
          <div className="block block--attention">
            <h3 className="block__title">Still unknown</h3>
            <p className="muted small">
              Read from what actually happened in this session, not from the advice text.
            </p>
            <ul className="list">
              {openQuestions.map((question) => (
                <li key={question.id}>
                  {question.question}{" "}
                  <span className={`tag tag--${question.status}`}>{question.status}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {shown && shown.open_unknowns.length > 0 && (
          <div className="block">
            <h3 className="block__title">Other open unknowns</h3>
            <ul className="list">
              {shown.open_unknowns.map((unknown, index) => (
                <li key={index}>{unknown}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </section>
  );
}
