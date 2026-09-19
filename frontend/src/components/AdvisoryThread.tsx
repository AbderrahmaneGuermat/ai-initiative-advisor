import { useEffect, useRef, useState } from "react";

import type { AnswerStatus, SessionView } from "../api/client";

const STATUS_LABEL: Record<AnswerStatus, string> = {
  answered: "answered",
  skipped: "skipped",
  unanswered: "not answered",
};

/**
 * Centre region: the advisory exchange.
 *
 * Which step happens next is decided by the backend, so this renders whatever
 * arrived rather than assuming a sequence.
 *
 * **A question's status is not the same as whether it awaits a reply.** Whether
 * the manager can still answer is a property of the round, reported as
 * `awaiting_response`. Once a round is submitted, an unanswered question in it
 * is an open unknown, and the form for it goes away.
 *
 * Detail lives in expandable sections. Nothing is truncated: the full text and
 * every source stay one click away.
 */
export default function AdvisoryThread({
  session,
  busy,
  onSubmitAnswers,
  onContinue,
  onGoToAdvice,
}: {
  session: SessionView | null;
  busy: string | null;
  onSubmitAnswers: (answers: Record<string, string>, skipped: string[]) => void;
  onContinue: () => void;
  onGoToAdvice: () => void;
}) {
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [skipped, setSkipped] = useState<Set<string>>(new Set());
  const [submitting, setSubmitting] = useState(false);

  const questionsRef = useRef<HTMLHeadingElement>(null);
  const previousPending = useRef(0);

  useEffect(() => {
    setDrafts({});
    setSkipped(new Set());
    setSubmitting(false);
  }, [session?.session_id]);

  // Editable because the round is open, not because the question is blank.
  const awaitingReply = session?.questions.filter((q) => q.awaiting_response) ?? [];
  const settled = session?.questions.filter((q) => !q.awaiting_response) ?? [];
  const roundPending = session?.awaiting_answers ?? false;
  const comparisonOutdated = session?.comparison_status === "outdated";

  // The request has returned, so the control is live again.
  useEffect(() => {
    if (busy === null) setSubmitting(false);
  }, [busy]);

  // Move focus to a new round of questions when it arrives, so the manager is
  // not left looking at the part of the page they were already reading.
  useEffect(() => {
    const count = awaitingReply.length;
    if (count > 0 && previousPending.current === 0 && busy === null) {
      questionsRef.current?.focus();
    }
    previousPending.current = count;
  }, [awaitingReply.length, busy]);

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
    if (submitting || busy !== null) return; // no duplicate submissions
    setSubmitting(true);
    const answers: Record<string, string> = {};
    for (const [id, text] of Object.entries(drafts)) {
      if (text.trim() && !skipped.has(id)) answers[id] = text.trim();
    }
    onSubmitAnswers(answers, [...skipped]);
  };

  const working = busy !== null || submitting;

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
        {/* One announcement region for the whole panel. Says only what the
            application knows: that a step is running, or which step finished.
            No percentages, no invented stages. */}
        <p className="visually-hidden" role="status" aria-live="polite">
          {busy
            ? `${busy}. This can take up to a minute.`
            : session?.recommendation
              ? "A recommendation is ready."
              : roundPending
                ? "The advisor has asked some questions."
                : ""}
        </p>

        {busy && (
          <div className="notice notice--busy">
            <span className="spinner" aria-hidden="true" />
            {busy}… This can take up to a minute.
          </div>
        )}

        {!session && !busy && (
          <p className="muted">
            Review the brief on the left, then start an advisory session. The advisor reads the
            brief, asks what it needs to, and works from there.
          </p>
        )}

        {session?.recommendation && !busy && (
          <button className="button button--jump" onClick={onGoToAdvice}>
            A recommendation is ready. Go to it →
          </button>
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

            <details className="section section--inline">
              <summary className="section__summary">
                What the advisor noticed in the brief
                <span className="section__hint">
                  {session.diagnosis.gaps.length +
                    session.diagnosis.contradictions.length +
                    session.diagnosis.unstated_assumptions.length}{" "}
                  findings
                </span>
              </summary>
              <div className="section__body">
                <FindingList label="Gaps" items={session.diagnosis.gaps} />
                <FindingList label="Contradictions" items={session.diagnosis.contradictions} />
                <FindingList
                  label="Unstated assumptions"
                  items={session.diagnosis.unstated_assumptions}
                />
              </div>
            </details>
          </article>
        )}

        {session && session.questions.length > 0 && (
          <article className="block">
            <h3 className="block__title" tabIndex={-1} ref={questionsRef}>
              Clarification
            </h3>

            {settled.map((question) => (
              <div className="question question--settled" key={question.id}>
                <div className="question__head">
                  <p className="question__text">{question.question}</p>
                  <span className={`tag tag--${question.status}`}>
                    {STATUS_LABEL[question.status]}
                  </span>
                </div>
                {question.answer && (
                  <div className="answer">
                    <span className="answer__label">You answered</span>
                    <p className="answer__text">{question.answer}</p>
                  </div>
                )}
              </div>
            ))}

            {settled.length > 0 && (
              <p className="muted small">
                <em>Answered</em> means you replied. It does not mean the reply was checked, or
                that the gap the question was about is closed. Anything still open is listed
                under <em>Still unknown</em>.
              </p>
            )}

            {settled.some((q) => q.status === "unanswered") && (
              <p className="muted small">
                Questions marked <em>not answered</em> were part of a round you have already sent.
                They stay here as open unknowns. Nothing further is needed from you.
              </p>
            )}

            {awaitingReply.map((question) => (
              <div className="question" key={question.id}>
                <p className="question__text">{question.question}</p>
                <p className="question__why">{question.why_it_matters}</p>
                <textarea
                  className="field__input field__input--area"
                  rows={3}
                  placeholder="Your answer, or skip"
                  aria-label={question.question}
                  disabled={skipped.has(question.id) || working}
                  value={drafts[question.id] ?? ""}
                  onChange={(event) =>
                    setDrafts((current) => ({ ...current, [question.id]: event.target.value }))
                  }
                />
                <label className="checkbox">
                  <input
                    type="checkbox"
                    checked={skipped.has(question.id)}
                    disabled={working}
                    onChange={() => toggleSkip(question.id)}
                  />
                  Skip this question
                </label>
              </div>
            ))}

            {roundPending && (
              <>
                <p className="muted small">
                  Anything you leave blank stays an open unknown. It is carried into the advice
                  rather than guessed at. Sending completes this round.
                </p>
                {/* The indicator sits beside the control, so it is visible from
                    wherever the manager pressed the button. */}
                <div className="submit-row">
                  <button className="button button--primary" onClick={submit} disabled={working}>
                    {working ? "Sending…" : "Send answers"}
                  </button>
                  {working && (
                    <span className="submit-row__status">
                      <span className="spinner" aria-hidden="true" />
                      Working. This can take up to a minute.
                    </span>
                  )}
                </div>
              </>
            )}
          </article>
        )}

        {session?.comparison && (
          <article className="block">
            <h3 className="block__title">Comparison</h3>

            {comparisonOutdated && (
              <div className="notice notice--stale">
                <strong>Awaiting update.</strong> You have answered something since this comparison
                was made, so it no longer reflects what the advisor knows. Select{" "}
                <em>Continue</em> to refresh it before new advice is built on it.
              </div>
            )}

            {session.comparison.criteria_considered.length > 0 && (
              <details className="section section--inline">
                <summary className="section__summary">
                  What it was judged on
                  <span className="section__hint">
                    {session.comparison.criteria_considered.length} criteria
                  </span>
                </summary>
                <div className="section__body">
                  <ul className="list">
                    {session.comparison.criteria_considered.map((criterion, index) => (
                      <li key={index}>{criterion}</li>
                    ))}
                  </ul>
                </div>
              </details>
            )}

            {session.comparison.initiatives.map((entry) => {
              const initiative = session.brief.initiatives.find(
                (i) => i.id === entry.initiative_id,
              );
              const unknowns = entry.missing_evidence.length;
              const evidence =
                entry.stated_facts.length +
                entry.assumptions.length +
                entry.feasibility_constraints.length +
                entry.trade_offs.length;
              return (
                <details className="section section--inline" key={entry.initiative_id}>
                  <summary className="section__summary">
                    {initiative?.name ?? entry.initiative_id}
                    <span className="section__hint">
                      {evidence} points · {unknowns} unknown
                    </span>
                  </summary>
                  <div className="section__body">
                    <ClaimList label="Stated facts" claims={entry.stated_facts} />
                    <ClaimList label="Assumptions" claims={entry.assumptions} assumption />
                    {unknowns > 0 && (
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
                </details>
              );
            })}
          </article>
        )}

        {session && !busy && !roundPending && !session.recommendation && (
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
