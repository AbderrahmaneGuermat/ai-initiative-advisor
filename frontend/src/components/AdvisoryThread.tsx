import { useEffect, useState } from "react";

import type { SessionView } from "../api/client";

/**
 * Centre region: the advisory exchange.
 *
 * Diagnosis, requests for information, clarification questions and the
 * comparison, in the order they actually happened. Which step happens next is
 * decided by the backend, so this component renders whatever arrived rather
 * than assuming a sequence.
 */
export default function AdvisoryThread({
  session,
  busy,
  onSubmitAnswers,
  onContinue,
}: {
  session: SessionView | null;
  busy: string | null;
  onSubmitAnswers: (answers: Record<string, string>, skipped: string[]) => void;
  onContinue: () => void;
}) {
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [skipped, setSkipped] = useState<Set<string>>(new Set());

  // Clear the form when a new session replaces the old one.
  useEffect(() => {
    setDrafts({});
    setSkipped(new Set());
  }, [session?.session_id]);

  const pending = session?.questions.filter((q) => q.status === "unanswered") ?? [];

  const toggleSkip = (id: string) => {
    setSkipped((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
    setDrafts((current) => ({ ...current, [id]: "" }));
  };

  const submit = () => {
    const answers: Record<string, string> = {};
    for (const [id, text] of Object.entries(drafts)) {
      if (text.trim() && !skipped.has(id)) answers[id] = text.trim();
    }
    onSubmitAnswers(answers, [...skipped]);
  };

  return (
    <section className="panel panel--thread" aria-labelledby="thread-heading">
      <div className="panel__header">
        <h2 id="thread-heading" className="panel__title">
          Advisory thread
        </h2>
        <p className="panel__hint">
          Diagnosis, questions and comparison, in whatever order the situation called for
        </p>
      </div>

      <div className="panel__body">
        {busy && (
          <div className="notice notice--busy" role="status">
            <span className="spinner" aria-hidden="true" />
            {busy}…
          </div>
        )}

        {!session && !busy && (
          <p className="muted">
            Review the brief on the left, then start an advisory session. The advisor reads the
            brief, asks what it needs to, and works from there.
          </p>
        )}

        {session?.context_request && (
          <article className="block block--attention">
            <h3 className="block__title">More information needed</h3>
            <p>{session.context_request.message}</p>
            <ul className="list">
              {session.context_request.missing.map((item) => (
                <li key={item.field}>
                  <strong>{item.field}.</strong> {item.why_required}
                </li>
              ))}
            </ul>
          </article>
        )}

        {session?.diagnosis && (
          <article className="block">
            <h3 className="block__title">Diagnosis</h3>
            <p>{session.diagnosis.summary}</p>

            <FindingList label="Gaps" items={session.diagnosis.gaps} />
            <FindingList label="Contradictions" items={session.diagnosis.contradictions} />
            <FindingList
              label="Unstated assumptions"
              items={session.diagnosis.unstated_assumptions}
            />
          </article>
        )}

        {session && session.questions.length > 0 && (
          <article className="block">
            <h3 className="block__title">Clarification</h3>

            {session.questions
              .filter((q) => q.status !== "unanswered")
              .map((question) => (
                <div className="question question--settled" key={question.id}>
                  <p className="question__text">{question.question}</p>
                  <span className={`tag tag--${question.status}`}>{question.status}</span>
                </div>
              ))}

            {pending.map((question) => (
              <div className="question" key={question.id}>
                <p className="question__text">{question.question}</p>
                <p className="question__why">{question.why_it_matters}</p>
                <textarea
                  className="field__input field__input--area"
                  rows={2}
                  placeholder="Your answer, or skip"
                  disabled={skipped.has(question.id)}
                  value={drafts[question.id] ?? ""}
                  onChange={(event) =>
                    setDrafts((current) => ({ ...current, [question.id]: event.target.value }))
                  }
                />
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={skipped.has(question.id)}
                    onChange={() => toggleSkip(question.id)}
                  />
                  Skip this question
                </label>
              </div>
            ))}

            {pending.length > 0 && (
              <>
                <p className="muted small">
                  Anything you leave blank stays an open unknown. It is carried into the advice
                  rather than guessed at.
                </p>
                <button className="button button--primary" onClick={submit} disabled={busy !== null}>
                  Send answers
                </button>
              </>
            )}
          </article>
        )}

        {session?.comparison && (
          <article className="block">
            <h3 className="block__title">Comparison</h3>

            {session.comparison.criteria_considered.length > 0 && (
              <p className="muted small">
                Judged on: {session.comparison.criteria_considered.join("; ")}.
              </p>
            )}

            {session.comparison.initiatives.map((entry) => {
              const initiative = session.brief.initiatives.find(
                (i) => i.id === entry.initiative_id,
              );
              return (
                <div className="compare" key={entry.initiative_id}>
                  <h4 className="compare__name">{initiative?.name ?? entry.initiative_id}</h4>
                  <ClaimList label="Stated facts" claims={entry.stated_facts} />
                  <ClaimList label="Assumptions" claims={entry.assumptions} assumption />
                  {entry.missing_evidence.length > 0 && (
                    <div className="claims">
                      <span className="claims__label">Not known</span>
                      <ul className="list">
                        {entry.missing_evidence.map((item, index) => (
                          <li key={index}>
                            {item.description} <em>{item.why_it_matters}</em>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <ClaimList label="Constraints" claims={entry.feasibility_constraints} />
                  <ClaimList label="Trade-offs" claims={entry.trade_offs} />
                </div>
              );
            })}
          </article>
        )}

        {session && !busy && !session.awaiting_answers && !session.recommendation && (
          <button className="button" onClick={onContinue}>
            Continue
          </button>
        )}
      </div>
    </section>
  );
}

function FindingList({
  label,
  items,
}: {
  label: string;
  items: { description: string; why_it_matters: string }[];
}) {
  if (items.length === 0) return null;
  return (
    <div className="claims">
      <span className="claims__label">{label}</span>
      <ul className="list">
        {items.map((item, index) => (
          <li key={index}>
            {item.description} <em>{item.why_it_matters}</em>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ClaimList({
  label,
  claims,
  assumption,
}: {
  label: string;
  claims: { statement: string; sources: { kind: string; ref_id: string }[] }[];
  assumption?: boolean;
}) {
  if (claims.length === 0) return null;
  return (
    <div className="claims">
      <span className="claims__label">{label}</span>
      <ul className="list">
        {claims.map((claim, index) => (
          <li key={index}>
            {claim.statement}
            {assumption && <span className="tag tag--assumption">assumption</span>}
            {claim.sources.length > 0 && (
              <span className="sources">
                {claim.sources.map((source) => source.ref_id).join(", ")}
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
