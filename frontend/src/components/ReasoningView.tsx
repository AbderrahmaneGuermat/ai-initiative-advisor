import type { Claim, SessionView } from "../api/client";
import { STANCE_LABEL, initiativeName, readableSource } from "../lookup";
import RefText from "./RefText";

/**
 * Reasoning and sources: everything the advice was built from.
 *
 * Nothing here is a summary written by this component. Every section renders
 * the records the backend holds, so what a reader checks is what the advisor
 * actually produced.
 *
 * **The separation the whole product rests on is preserved visually.** What the
 * manager supplied is marked as theirs. What the advisor assumed is marked as an
 * assumption and carries no sources, which is the signal. What is not known is
 * stated as not known rather than softened into a weak finding.
 */

function ClaimList({
  label,
  claims,
  session,
  assumption,
}: {
  label: string;
  claims: Claim[];
  session: SessionView;
  assumption?: boolean;
}) {
  if (claims.length === 0) return null;
  return (
    <div className="evidence">
      <span className="micro-label">{label}</span>
      <ul className="evidence__list">
        {claims.map((claim, index) => (
          <li key={index} className={assumption ? "evidence__item is-assumption" : "evidence__item"}>
            <span className="evidence__text">
              <RefText text={claim.statement} />
            </span>
            {assumption && <span className="tag-soft">assumption</span>}
            {claim.sources.length > 0 && (
              <span className="evidence__sources">
                {claim.sources.map((ref, i) => {
                  const r = readableSource(session, ref);
                  return (
                    <span className="ref" key={i} title={`${r.kind} · ${r.id}`}>
                      {r.kind}: {r.label} <code className="ref__id">{r.id}</code>
                    </span>
                  );
                })}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function ReasoningView({ session }: { session: SessionView }) {
  const { diagnosis, comparison } = session;
  const recommendation = session.recommendation ?? session.previous_recommendation;
  const answered = session.questions.filter((q) => q.status === "answered");
  const notAnswered = session.questions.filter((q) => q.status !== "answered");

  return (
    <div className="reasoning">
      {session.questions.length > 0 && (
        <section className="block">
          <h3 className="block__title">What you told the advisor</h3>
          <p className="muted small">
            Answered means you replied. It does not mean the reply was checked, or that the gap the
            question was about is closed.
          </p>

          {answered.map((question) => (
            <div className="qa" key={question.id}>
              <p className="qa__q">{question.question}</p>
              {question.answer && <p className="qa__a">{question.answer}</p>}
              <span className="status status--answered">You answered</span>
            </div>
          ))}

          {notAnswered.length > 0 && (
            <ul className="opens">
              {notAnswered.map((question) => (
                <li className="open-row" key={question.id}>
                  <span className="open-row__text">{question.question}</span>
                  <span className={`status status--${question.status}`}>
                    {question.status === "skipped" ? "You skipped this" : "Not answered"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}

      {diagnosis && (
        <section className="block">
          <h3 className="block__title">Reading of the brief</h3>
          <p className="prose">
            <RefText text={diagnosis.summary} />
          </p>

          {(["gaps", "contradictions", "unstated_assumptions"] as const).map((key) => {
            const items = diagnosis[key];
            if (items.length === 0) return null;
            const label =
              key === "gaps"
                ? "Gaps"
                : key === "contradictions"
                  ? "Contradictions"
                  : "Unstated assumptions";
            return (
              <details className="disclose disclose--wide" key={key}>
                <summary className="disclose__summary">
                  {label}
                  <span className="disclose__count">{items.length}</span>
                </summary>
                <ul className="disclose__list">
                  {items.map((item, index) => (
                    <li key={index}>
                      <strong className="finding">
                        <RefText text={item.description} />
                      </strong>
                      <span className="finding__why">
                        <RefText text={item.why_it_matters} />
                      </span>
                      {item.relates_to.length > 0 && (
                        <span className="evidence__sources">
                          {item.relates_to.map((ref, i) => {
                            const r = readableSource(session, ref);
                            return (
                              <span className="ref" key={i} title={`${r.kind} · ${r.id}`}>
                                {r.kind}: {r.label} <code className="ref__id">{r.id}</code>
                              </span>
                            );
                          })}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </details>
            );
          })}
        </section>
      )}

      {comparison && (
        <section className="block">
          <h3 className="block__title">How the options compare</h3>

          {session.comparison_status === "outdated" && (
            <p className="notice notice--warn">
              <strong>Awaiting update.</strong> You have answered something since this comparison
              was made, so it no longer reflects what the advisor knows.
            </p>
          )}

          {comparison.criteria_considered.length > 0 && (
            <details className="disclose disclose--wide">
              <summary className="disclose__summary">
                What it was judged on
                <span className="disclose__count">{comparison.criteria_considered.length}</span>
              </summary>
              <ul className="disclose__list">
                {comparison.criteria_considered.map((criterion, index) => (
                  <li key={index}>
                    <RefText text={criterion} />
                  </li>
                ))}
              </ul>
            </details>
          )}

          {comparison.initiatives.map((entry) => (
            <details className="disclose disclose--wide" key={entry.initiative_id}>
              <summary className="disclose__summary">
                {initiativeName(session, entry.initiative_id)}
                <span className="disclose__count">
                  {entry.missing_evidence.length} unknown
                </span>
              </summary>
              <div className="disclose__body">
                <ClaimList
                  label="What you told us"
                  claims={entry.stated_facts}
                  session={session}
                />
                <ClaimList
                  label="What the advisor assumed"
                  claims={entry.assumptions}
                  session={session}
                  assumption
                />
                {entry.missing_evidence.length > 0 && (
                  <div className="evidence">
                    <span className="micro-label">Not known</span>
                    <ul className="evidence__list">
                      {entry.missing_evidence.map((item, index) => (
                        <li className="evidence__item" key={index}>
                          <span className="evidence__text">
                            <RefText text={item.description} />
                          </span>
                          <span className="finding__why">
                            <RefText text={item.why_it_matters} />
                          </span>
                          {item.how_it_could_be_resolved && (
                            <span className="finding__why">
                              How to find out: <RefText text={item.how_it_could_be_resolved} />
                            </span>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
                <ClaimList
                  label="Limits that apply"
                  claims={entry.feasibility_constraints}
                  session={session}
                />
                <ClaimList
                  label="What it gives up"
                  claims={entry.trade_offs}
                  session={session}
                />
              </div>
            </details>
          ))}

          {comparison.cross_cutting_notes.length > 0 && (
            <ClaimList
              label="True of the whole situation"
              claims={comparison.cross_cutting_notes}
              session={session}
            />
          )}
        </section>
      )}

      {recommendation && (
        <section className="block">
          <h3 className="block__title">The advice, in full</h3>

          {recommendation.items.map((item) => (
            <div className="qa" key={item.initiative_id}>
              <p className="qa__q">
                {initiativeName(session, item.initiative_id)} — {STANCE_LABEL[item.stance]}
              </p>
              <p className="prose">
                <RefText text={item.rationale} />
              </p>
              {item.rests_on_assumptions.length > 0 && (
                <ul className="disclose__list">
                  {item.rests_on_assumptions.map((condition, index) => (
                    <li key={index}>
                      <RefText text={condition} />
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}

          {recommendation.risks.length > 0 && (
            <details className="disclose disclose--wide">
              <summary className="disclose__summary">
                What could make this wrong
                <span className="disclose__count">{recommendation.risks.length}</span>
              </summary>
              <ul className="disclose__list">
                {recommendation.risks.map((risk, index) => (
                  <li key={index}>
                    <strong className="finding">
                      <RefText text={risk.description} />
                    </strong>
                    <span className="finding__why">
                      <RefText text={risk.consequence_if_realised} />
                    </span>
                    {risk.early_signal && (
                      <span className="finding__why">Early signal: <RefText text={risk.early_signal} /></span>
                    )}
                  </li>
                ))}
              </ul>
            </details>
          )}

          <div className="evidence">
            <span className="micro-label">How far to trust this</span>
            <p className="prose">
              <RefText text={recommendation.confidence_note} />
            </p>
          </div>
        </section>
      )}
    </div>
  );
}
