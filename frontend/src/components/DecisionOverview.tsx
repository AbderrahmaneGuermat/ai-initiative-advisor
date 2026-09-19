import { useId, useState } from "react";

import type { RecommendedItem, SessionView } from "../api/client";
import { STANCE_LABEL, initiativeName, priorityIsExplicit, readableSource } from "../lookup";
import RefText from "./RefText";
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
 * **The recommendation is the headline.** The initiative's name is the largest
 * text on the card. The advisor's overall summary is the page description,
 * in full and at body size (see App), so it frames the reading without
 * pushing the recommendation off the screen.
 *
 * **Prominence follows disposition, not position.** Every option the advisor
 * recommended gets a lead card; the rest sit in quieter cards. The advisor's
 * list order, which its prompt says carries priority, is kept within each
 * group, but no item is labelled "first": the order is not validated and no
 * field states it (D-048). If nothing is recommended, that is shown as the
 * finding it is.
 *
 * **Conditions stay beside the advice; provenance is one step away.** What a
 * recommendation holds only if is visible in the card. The sources it cites,
 * each with its identifier, are behind "Evidence & sources". Nothing is
 * dropped, trimmed or summarised.
 */

const STANCE_ICON = {
  recommended: CheckIcon,
  consider_later: ClockIcon,
  not_recommended: MinusCircleIcon,
  insufficient_information: QuestionIcon,
} as const;

function StanceTag({ stance, plain }: { stance: RecommendedItem["stance"]; plain?: boolean }) {
  const Icon = STANCE_ICON[stance];
  return (
    <span className={plain ? `stance-plain stance-plain--${stance}` : `stance stance--${stance}`}>
      <Icon size={13} />
      {STANCE_LABEL[stance]}
    </span>
  );
}

function EvidenceList({ item, session }: { item: RecommendedItem; session: SessionView }) {
  return (
    <ul className="sources">
      {item.supported_by.map((ref, index) => {
        const r = readableSource(session, ref);
        return (
          <li className="sources__item" key={index}>
            <span className="sources__kind">{r.kind}</span>
            <span className="sources__label">{r.label}</span>
            <code className="sources__id">{r.id}</code>
          </li>
        );
      })}
    </ul>
  );
}

type FirstActions = NonNullable<SessionView["recommendation"]>["first_actions"];

function LeadCard({
  item,
  session,
  onExplain,
  firstActions,
}: {
  item: RecommendedItem;
  session: SessionView;
  onExplain: () => void;
  firstActions: FirstActions;
}) {
  const [panel, setPanel] = useState<"none" | "actions" | "evidence">("none");
  const actionsId = useId();
  const evidenceId = useId();
  const toggle = (which: "actions" | "evidence") =>
    setPanel((current) => (current === which ? "none" : which));

  return (
    <article className="lead">
      <div className="lead__head">
        <StanceTag stance={item.stance} />
        {priorityIsExplicit() && <span className="lead__rank">Recommended first</span>}
      </div>

      <h2 className="lead__name">{initiativeName(session, item.initiative_id)}</h2>
      <p className="lead__why">
        <RefText text={item.rationale} />
      </p>

      {item.rests_on_assumptions.length > 0 && (
        <div className="lead__conditions">
          <span className="lead__conditions-label">Holds only if</span>
          <ul>
            {item.rests_on_assumptions.map((condition, index) => (
              <li key={index}>
                <AlertIcon size={14} />
                <span>
                  <RefText text={condition} />
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="lead__actions">
        {firstActions.length > 0 && (
          <button
            type="button"
            className="button button--primary"
            aria-expanded={panel === "actions"}
            aria-controls={actionsId}
            onClick={() => toggle("actions")}
          >
            {panel === "actions" ? "Hide first actions" : "See first actions"}
            <ChevronIcon size={14} className={panel === "actions" ? "rot-up" : "rot90"} />
          </button>
        )}
        <button type="button" className="text-link" onClick={onExplain}>
          Why this recommendation
        </button>
        {item.supported_by.length > 0 && (
          <button
            type="button"
            className="text-link text-link--quiet"
            aria-expanded={panel === "evidence"}
            aria-controls={evidenceId}
            onClick={() => toggle("evidence")}
          >
            Evidence &amp; sources ({item.supported_by.length})
          </button>
        )}
      </div>

      {panel === "actions" && (
        <div className="lead__panel" id={actionsId}>
          <h3 className="lead__panel-title">First actions</h3>
          <ol className="steps">
            {firstActions.map((action, index) => (
              <li key={index} className="steps__item">
                <span className="steps__text">
                  <RefText text={action.action} />
                </span>
                <span className="steps__purpose">
                  <RefText text={action.purpose} />
                </span>
                {action.resolves_unknown && (
                  <span className="steps__closes">
                    Closes: <RefText text={action.resolves_unknown} />
                  </span>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}

      {panel === "evidence" && (
        <div className="lead__panel" id={evidenceId}>
          <h3 className="lead__panel-title">What this recommendation cites</h3>
          <EvidenceList item={item} session={session} />
        </div>
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
  const moreId = useId();

  const recommendation = session.recommendation ?? session.previous_recommendation;
  if (!recommendation) return null;

  const lead = recommendation.items.filter((i) => i.stance === "recommended");
  const others = recommendation.items.filter((i) => i.stance !== "recommended");
  const open = session.questions.filter((q) => q.status !== "answered");

  return (
    <div className="overview">
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
          <div className="lead__head">
            <StanceTag stance="insufficient_information" />
          </div>
          <h2 className="lead__name">Nothing is recommended yet</h2>
          <p className="lead__why">
            The advisor did not put any option forward. Each one below says why, and the open
            questions are listed underneath.
          </p>
          <div className="lead__actions">
            <button type="button" className="text-link" onClick={onExplain}>
              See the reasoning
              <ArrowRightIcon size={14} />
            </button>
          </div>
        </div>
      )}

      {others.length > 0 && (
        <section className="block">
          <div className="block__head">
            <h3 className="block__title">
              {lead.length > 0 ? "Keep the other options in view" : "The options considered"}
            </h3>
            <span className="block__aside">
              {others.length} {others.length === 1 ? "option" : "options"}
            </span>
          </div>
          <div className="cards">
            {others.map((item) => (
              <article className="card" key={item.initiative_id}>
                <StanceTag stance={item.stance} plain />
                <h4 className="card__name">{initiativeName(session, item.initiative_id)}</h4>
                <p className="card__why">
                  <RefText text={item.rationale} />
                </p>
                {(item.rests_on_assumptions.length > 0 || item.supported_by.length > 0) && (
                  <details className="disclose">
                    <summary className="disclose__summary">
                      What this rests on
                      <span className="disclose__count">
                        {item.rests_on_assumptions.length + item.supported_by.length}
                      </span>
                    </summary>
                    <div className="disclose__body">
                      {item.rests_on_assumptions.length > 0 && (
                        <ul className="plain-list">
                          {item.rests_on_assumptions.map((condition, index) => (
                            <li key={index}>
                              <RefText text={condition} />
                            </li>
                          ))}
                        </ul>
                      )}
                      {item.supported_by.length > 0 && <EvidenceList item={item} session={session} />}
                    </div>
                  </details>
                )}
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="block">
        <div className="block__head">
          <h3 className="block__title">Confirm before committing</h3>
          <span className="block__aside">Uncertainty stays visible</span>
        </div>

        {open.length === 0 && recommendation.open_unknowns.length === 0 ? (
          <p className="muted">Nothing outstanding was recorded for this session.</p>
        ) : (
          <>
            {open.length > 0 && (
              <ul className="checks">
                {open.map((question) => (
                  <li className="checks__row" key={question.id}>
                    <span className="checks__icon" aria-hidden="true">
                      <QuestionIcon size={15} />
                    </span>
                    <span className="checks__text">{question.question}</span>
                    <span className={`status status--${question.status}`}>
                      {question.status === "skipped" ? "You skipped this" : "Not answered"}
                    </span>
                  </li>
                ))}
              </ul>
            )}

            {recommendation.open_unknowns.length > 0 && (
              <>
                <button
                  type="button"
                  className="text-link"
                  aria-expanded={showMore}
                  aria-controls={moreId}
                  onClick={() => setShowMore((v) => !v)}
                >
                  {showMore
                    ? "Hide the other open questions"
                    : `Review the other open questions (${recommendation.open_unknowns.length})`}
                </button>
                {showMore && (
                  <ul className="unknowns" id={moreId}>
                    {recommendation.open_unknowns.map((unknown, index) => (
                      <li key={index}>
                        <RefText text={unknown} />
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </>
        )}
      </section>

      <section className="block">
        <h3 className="block__title">How far to trust this</h3>
        <p className="prose">
          <RefText text={recommendation.confidence_note} />
        </p>
      </section>
    </div>
  );
}
