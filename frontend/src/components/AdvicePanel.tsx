import { forwardRef } from "react";

import type { SessionView, Stance } from "../api/client";

const STANCE_LABEL: Record<Stance, string> = {
  recommended: "Recommended",
  consider_later: "Consider later",
  not_recommended: "Not recommended",
  insufficient_information: "Not enough information",
};

/**
 * The standing advice.
 *
 * Scannable at a glance: the summary, every initiative's stance with its
 * reasoning, and what is still unknown. Supporting detail is one click away in
 * labelled sections, never truncated and never removed. Hiding uncertainty
 * would defeat the point of the product, so the unknowns stay in the open while
 * the workings fold away.
 *
 * Open questions are rendered from session state, never from the
 * recommendation's own summary, so advice that forgets to mention something the
 * manager skipped cannot make it disappear.
 */
const AdvicePanel = forwardRef<HTMLElement, { session: SessionView | null }>(
  function AdvicePanel({ session }, ref) {
    const recommendation = session?.recommendation ?? null;
    const outdated = session?.previous_recommendation ?? null;
    const openQuestions = session?.questions.filter((q) => q.status !== "answered") ?? [];
    const shown = recommendation ?? outdated;
    const isOutdated = recommendation === null && outdated !== null;

    return (
      <section className="panel panel--advice" aria-labelledby="advice-heading" ref={ref}>
        <div className="panel__header">
          <h2 id="advice-heading" className="panel__title" tabIndex={-1}>
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
              reference and is not the current recommendation. Select <em>Continue</em> to refresh
              it.
            </div>
          )}

          {shown && (
            <div className={isOutdated ? "advice advice--stale" : "advice"}>
              <p className="advice__summary">{shown.summary}</p>

              <ol className="shortlist">
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
                        <details className="section section--inline">
                          <summary className="section__summary">
                            What this rests on
                            <span className="section__hint">
                              {item.rests_on_assumptions.length} assumptions
                            </span>
                          </summary>
                          <div className="section__body">
                            <ul className="list">
                              {item.rests_on_assumptions.map((assumption, index) => (
                                <li key={index}>{assumption}</li>
                              ))}
                            </ul>
                          </div>
                        </details>
                      )}
                    </li>
                  );
                })}
              </ol>

              {/* Uncertainty stays visible. Workings fold away. */}
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

              {shown.open_unknowns.length > 0 && (
                <div className="block block--attention">
                  <h3 className="block__title">Other open unknowns</h3>
                  <ul className="list">
                    {shown.open_unknowns.map((unknown, index) => (
                      <li key={index}>{unknown}</li>
                    ))}
                  </ul>
                </div>
              )}

              {shown.first_actions.length > 0 && (
                <details className="section" open>
                  <summary className="section__summary">
                    First actions
                    <span className="section__hint">{shown.first_actions.length} steps</span>
                  </summary>
                  <div className="section__body">
                    <ol className="list">
                      {shown.first_actions.map((action, index) => (
                        <li key={index}>
                          {action.action} <em>{action.purpose}</em>
                        </li>
                      ))}
                    </ol>
                  </div>
                </details>
              )}

              {shown.risks.length > 0 && (
                <details className="section">
                  <summary className="section__summary">
                    Risks
                    <span className="section__hint">{shown.risks.length} named</span>
                  </summary>
                  <div className="section__body">
                    <ul className="list">
                      {shown.risks.map((risk, index) => (
                        <li key={index}>
                          {risk.description} <em>{risk.consequence_if_realised}</em>
                        </li>
                      ))}
                    </ul>
                  </div>
                </details>
              )}

              <details className="section">
                <summary className="section__summary">
                  How far to trust this
                  <span className="section__hint">The advisor's own caveats</span>
                </summary>
                <div className="section__body">
                  <p>{shown.confidence_note}</p>
                </div>
              </details>
            </div>
          )}

          {!shown && session && openQuestions.length > 0 && (
            <div className="block block--attention">
              <h3 className="block__title">Still unknown</h3>
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
        </div>
      </section>
    );
  },
);

export default AdvicePanel;
