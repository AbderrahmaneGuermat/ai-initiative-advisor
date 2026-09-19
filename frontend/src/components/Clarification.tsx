import { useEffect, useRef, useState } from "react";

import type { SessionView } from "../api/client";

/**
 * The clarification round.
 *
 * **Whether a question is editable is a property of the round, not of the
 * answer.** Once the manager submits, an unanswered question in that round is
 * an open unknown, not an outstanding request, so its form goes away and it
 * stays visible as a settled row. The three statuses remain distinct: answered,
 * skipped, and not answered.
 *
 * The progress indicator sits beside the button that started the work, because
 * a manager submitting from the bottom of a long list cannot see the top of the
 * page. The wait is described in words the application can stand behind: a step
 * is running, and it may take a few minutes. The turn deadline is a ceiling at
 * which work is abandoned, not a promise.
 */
export default function Clarification({
  session,
  busy,
  onSubmit,
}: {
  session: SessionView;
  busy: string | null;
  onSubmit: (answers: Record<string, string>, skipped: string[]) => void;
}) {
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [skipped, setSkipped] = useState<Set<string>>(new Set());
  const [submitting, setSubmitting] = useState(false);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const previousPending = useRef(0);

  useEffect(() => {
    setDrafts({});
    setSkipped(new Set());
    setSubmitting(false);
  }, [session.session_id]);

  useEffect(() => {
    if (busy === null) setSubmitting(false);
  }, [busy]);

  const pending = session.questions.filter((q) => q.awaiting_response);
  const settled = session.questions.filter((q) => !q.awaiting_response);
  const roundPending = session.awaiting_answers;
  const working = busy !== null || submitting;

  // A new round takes focus, so the manager is not left reading the part of the
  // page they had already finished with.
  useEffect(() => {
    if (pending.length > 0 && previousPending.current === 0 && busy === null) {
      headingRef.current?.focus();
    }
    previousPending.current = pending.length;
  }, [pending.length, busy]);

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
    if (working) return; // no duplicate submissions
    setSubmitting(true);
    const answers: Record<string, string> = {};
    for (const [id, text] of Object.entries(drafts)) {
      if (text.trim() && !skipped.has(id)) answers[id] = text.trim();
    }
    onSubmit(answers, [...skipped]);
  };

  if (session.questions.length === 0) return null;

  return (
    <section className="block" aria-labelledby="clarification-heading">
      <h3 className="block__title" id="clarification-heading" tabIndex={-1} ref={headingRef}>
        {roundPending ? "A few questions first" : "What you told the advisor"}
      </h3>

      {roundPending && (
        <p className="muted small">
          Answer what you can. Anything you leave blank stays an open unknown and is carried into
          the advice rather than guessed at.
        </p>
      )}

      {settled.map((question) => (
        <div className="qa" key={question.id}>
          <p className="qa__q">{question.question}</p>
          {question.answer && <p className="qa__a">{question.answer}</p>}
          <span className={`status status--${question.status}`}>
            {question.status === "answered"
              ? "You answered"
              : question.status === "skipped"
                ? "You skipped this"
                : "Not answered"}
          </span>
        </div>
      ))}

      {settled.some((q) => q.status === "unanswered") && (
        <p className="muted small">
          Questions marked <em>not answered</em> were part of a round you have already sent. They
          stay here as open unknowns. Nothing further is needed from you.
        </p>
      )}

      {pending.map((question) => (
        <div className="ask" key={question.id}>
          <p className="ask__q">{question.question}</p>
          <p className="ask__why">{question.why_it_matters}</p>
          <textarea
            className="input input--area"
            rows={3}
            placeholder="Your answer, or skip"
            aria-label={question.question}
            disabled={skipped.has(question.id) || working}
            value={drafts[question.id] ?? ""}
            onChange={(event) =>
              setDrafts((current) => ({ ...current, [question.id]: event.target.value }))
            }
          />
          <label className="check">
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
        <div className="submit-row">
          <button className="button button--primary" onClick={submit} disabled={working}>
            {working ? "Sending…" : "Send answers"}
          </button>
          {working && (
            <span className="submit-row__status">
              <span className="spinner" aria-hidden="true" />
              The advisor is working. This may take a few minutes.
            </span>
          )}
        </div>
      )}
    </section>
  );
}
