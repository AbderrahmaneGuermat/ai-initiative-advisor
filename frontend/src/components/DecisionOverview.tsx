import { useState } from "react";

import type { RecommendedItem, SessionView } from "../api/client";
import { STANCE_LABEL, initiativeName, priorityIsExplicit, readableSource } from "../lookup";
import {
  AlertIcon,
  ArrowRightIcon,
  CheckIcon,
  ChevronIcon,
  ClockIcon,
  MinusCircleIcon,
  QuestionIcon,
} from "./icons";

/**
 * The decision overview: what to do, what else was considered, what is still open.
 *
 * **Prominence follows disposition, not position.** Every option the advisor
 * recommended gets the lead card; the rest sit in quieter cards. Array order is
 * not read as a ranking, because the contract has no priority field and the
 * model was never asked to produce one. If the advice recommends nothing, that
 * is shown as the finding it is rather than promoting whatever happened to
 * come first.
 *
 * **Uncertainty is not decoration.** The skipped and unanswered questions sit
 * directly under the advice as compact rows, each stating its own status in
 * words. The advisor's other open unknowns are behind a counted disclosure:
 * available in full, and never merged, trimmed or summarised away.
 */

const STANCE_ICON = {
  recommended: CheckIcon,
  consider_later: ClockIcon,
  not_recommended: MinusCircleIcon,
  insufficient_information: QuestionIcon,
} as const;

function StanceTag({ stance }: { stance: RecommendedItem["stance"] }) {
  const Icon = STANCE_ICON[stance];
  return (
    <span className={`stance stance--${stance}`}>
      <Icon size={13} />
      {STANCE_LABEL[stance]}
    </span>
  );
}

function Sources({ item, session }: { item: RecommendedItem; session: SessionView }) {
  if (item.supported_by.length === 0) return null;
  return (
    <div className="lead__sources">
      <span className="micro-label">Based on</span>
      <ul className="chips">
        {item.supported_by.map((ref, index) => {
          const r = readableSource(session, ref);
          return (
            <li className="chip" key={index} title={`${r.kind} · ${r.id}`}>
              <span className="chip__kind">{r.kind}</span>
              <span className="chip__text">{r.label}</span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function LeadCard({
  item,
  session,
  onExplain,
  firstActions,
}: {
  item: RecommendedItem;
  session: SessionView;
  onExplain: () => void;
  firstActions: SessionView["recommendation"] extends null
    ? never
    : NonNullable<SessionView["recommendation"]>["first_actions"];
}) {
  const [showActions, setShowActions] = useState(false);

  return (
    <article className="lead">
      <div className="lead__head">
        <StanceTag stance={item.stance} />
        {priorityIsExplicit() && <span className="lead__rank">Recommended first</span>}
      </div>

      <h3 className="lead__name">{initiativeName(session, item.initiative_id)}</h3>
      <p className="lead__why">{item.rationale}</p>

      <Sources item={item} session={session} />

      {item.rests_on_assumptions.length > 0 && (
        <div className="conditions">
          <span className="micro-label">Holds only if</span>
          <ul className="conditions__list">
            {item.rests_on_assumptions.map((condition, index) => (
              <li key={index}>{condition}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="lead__actions">
        {firstActions.length > 0 && (
          <button
            type="button"
            className="button button--quiet"
            aria-expanded={showActions}
            onClick={() => setShowActions((v) => !v)}
          >
            <ChevronIcon size={14} className={showActions ? "rot90" : ""} />
            {showActions ? "Hide first actions" : "See first actions"}
          </button>
        )}
        <button type="button" className="button button--link" onClick={onExplain}>
          Why this recommendation
          <ArrowRightIcon size={14} />
        </button>
      </div>

      {showActions && firstActions.length > 0 && (
        <ol className="steps">
          {firstActions.map((action, index) => (
            <li key={index} className="steps__item">
              <span className="steps__text">{action.action}</span>
              <span className="steps__purpose">{action.purpose}</span>
              {action.resolves_unknown && (
                <span className="steps__closes">Closes: {action.resolves_unknown}</span>
              )}
            </li>
          ))}
        </ol>
      )}
    </article>
  );
}

export default function DecisionOverview({
  session,
  onExplain,
}: {
  session: SessionView;
  onExplain: () => void;
}) {
  const [showMore, setShowMore] = useState(false);

  const recommendation = session.recommendation ?? session.previous_recommendation;
  if (!recommendation) return null;

  const lead = recommendation.items.filter((i) => i.stance === "recommended");
  const others = recommendation.items.filter((i) => i.stance !== "recommended");
  const open = session.questions.filter((q) => q.status !== "answered");

  return (
    <div className="overview">
      <p className="summary">{recommendation.summary}</p>

      {lead.length > 0 ? (
        <div className="leads">
          {lead.map((item) => (
            <LeadCard
              key={item.initiative_id}
              item={item}
              session={session}
              onExplain={onExplain}
              firstActions={recommendation.first_actions}
            />
          ))}
        </div>
      ) : (
        <div className="lead lead--none">
          <StanceTag stance="insufficient_information" />
          <h3 className="lead__name">Nothing is recommended yet</h3>
          <p className="lead__why">
            The advisor did not put any option forward. Each one below says why, and the open
            questions are listed underneath.
          </p>
          <div className="lead__actions">
            <button type="button" className="button button--link" onClick={onExplain}>
              See the reasoning
              <ArrowRightIcon size={14} />
            </button>
          </div>
        </div>
      )}

      {others.length > 0 && (
        <section className="block">
          <h3 className="block__title">Other initiatives</h3>
          <div className="cards">
            {others.map((item) => (
              <article className="card" key={item.initiative_id}>
                <StanceTag stance={item.stance} />
                <h4 className="card__name">{initiativeName(session, item.initiative_id)}</h4>
                <p className="card__why">{item.rationale}</p>
                {item.rests_on_assumptions.length > 0 && (
                  <details className="disclose">
                    <summary className="disclose__summary">
                      What this rests on
                      <span className="disclose__count">
                        {item.rests_on_assumptions.length}
                      </span>
                    </summary>
                    <ul className="disclose__list">
                      {item.rests_on_assumptions.map((condition, index) => (
                        <li key={index}>{condition}</li>
                      ))}
                    </ul>
                  </details>
                )}
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="block">
        <h3 className="block__title">Confirm before committing</h3>

        {open.length === 0 && recommendation.open_unknowns.length === 0 ? (
          <p className="muted">Nothing outstanding was recorded for this session.</p>
        ) : (
          <>
            {open.length > 0 && (
              <ul className="opens">
                {open.map((question) => (
                  <li className="open-row" key={question.id}>
                    <span className="open-row__icon" aria-hidden="true">
                      <AlertIcon size={14} />
                    </span>
                    <span className="open-row__text">{question.question}</span>
                    <span className={`status status--${question.status}`}>
                      {question.status === "skipped" ? "You skipped this" : "Not answered"}
                    </span>
                  </li>
                ))}
              </ul>
            )}

            {recommendation.open_unknowns.length > 0 && (
              <details
                className="disclose disclose--wide"
                open={showMore}
                onToggle={(e) => setShowMore((e.target as HTMLDetailsElement).open)}
              >
                <summary className="disclose__summary">
                  Everything else the advisor flagged as unknown
                  <span className="disclose__count">{recommendation.open_unknowns.length}</span>
                </summary>
                <ul className="disclose__list">
                  {recommendation.open_unknowns.map((unknown, index) => (
                    <li key={index}>{unknown}</li>
                  ))}
                </ul>
              </details>
            )}
          </>
        )}
      </section>

      <section className="block">
        <h3 className="block__title">How far to trust this</h3>
        <p className="prose">{recommendation.confidence_note}</p>
      </section>
    </div>
  );
}
