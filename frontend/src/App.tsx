import { useCallback, useEffect, useRef, useState } from "react";

import {
  ApiError,
  continueSession,
  fetchHealth,
  fetchScenario,
  fetchSession,
  startSession,
  submitAnswers,
  type AdvisoryError,
  type Brief,
  type ConnectionState,
  type SessionView,
} from "./api/client";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import Clarification from "./components/Clarification";
import DecisionOverview from "./components/DecisionOverview";
import ReasoningView from "./components/ReasoningView";
import ClampText from "./components/ClampText";
import RefText, { RefProvider } from "./components/RefText";
import { AlertIcon, BookIcon } from "./components/icons";
import "./styles/layout.css";

function sessionFromUrl(): string | null {
  const value = new URLSearchParams(window.location.search).get("session");
  return value && value.trim() ? value.trim() : null;
}

function rememberInUrl(sessionId: string): void {
  const url = new URL(window.location.href);
  if (url.searchParams.get("session") === sessionId) return;
  url.searchParams.set("session", sessionId);
  window.history.replaceState({}, "", url.toString());
}

type Recovery =
  | { kind: "none" }
  | { kind: "loading"; id: string }
  | { kind: "restored"; id: string }
  | { kind: "missing"; id: string };

type View = "overview" | "reasoning";

/**
 * Application shell.
 *
 * Layout: a compact context sidebar and one main column. The main column shows
 * whatever the session most needs attention on. While a clarification round is
 * open, the form is the first thing in it, so the manager is never scrolling
 * past an empty advice panel to reach the thing being asked of them.
 *
 * **Reopening a session.** `?session=<id>` fetches that session and restores it.
 * A session created here writes its identifier into the URL. This recovers
 * in-memory backend state; it is not persistence, and a backend restart loses
 * every session. Recovery issues one GET and never runs the advisor.
 *
 * Nothing in this file decides anything advisory. Switching views, expanding a
 * section and reopening a session are all local or read-only.
 */
export default function App() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "checking" });
  const [brief, setBrief] = useState<Brief | null>(null);
  const [session, setSession] = useState<SessionView | null>(null);
  const [briefEdited, setBriefEdited] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<AdvisoryError | null>(null);
  const [view, setView] = useState<View>("overview");
  const [scenarioFailed, setScenarioFailed] = useState(false);
  const [recovery, setRecovery] = useState<Recovery>(() => {
    const id = sessionFromUrl();
    return id ? { kind: "loading", id } : { kind: "none" };
  });

  const headingRef = useRef<HTMLHeadingElement>(null);
  const hadRecommendation = useRef(false);

  useEffect(() => {
    const controller = new AbortController();

    fetchHealth(controller.signal)
      .then((health) => setConnection({ kind: "connected", health }))
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === "AbortError") return;
        setConnection({
          kind: "failed",
          message: cause instanceof Error ? cause.message : "Unknown error",
        });
      });

    const requested = sessionFromUrl();

    if (requested) {
      // The sample scenario is not requested on this path, so it cannot
      // overwrite a restored brief.
      fetchSession(requested)
        .then((restored) => {
          setSession(restored);
          setBrief(restored.brief);
          setBriefEdited(false);
          setRecovery({ kind: "restored", id: requested });
          if (restored.error) setError(restored.error);
        })
        .catch(() => setRecovery({ kind: "missing", id: requested }));
      return () => controller.abort();
    }

    fetchScenario()
      .then((scenario) => setBrief(scenario.brief))
      .catch(() => setScenarioFailed(true));

    return () => controller.abort();
  }, []);

  // When advice arrives, move focus to the brief's heading. Attention is
  // wherever the manager last acted, which is rarely where the answer landed.
  useEffect(() => {
    const has = Boolean(session?.recommendation);
    if (has && !hadRecommendation.current && busy === null) {
      setView("overview");
      headingRef.current?.focus();
    }
    hadRecommendation.current = has;
  }, [session?.recommendation, busy]);

  const guard = useCallback(async (label: string, work: () => Promise<SessionView>) => {
    setBusy(label);
    setError(null);
    try {
      const next = await work();
      setSession(next);
      setBrief(next.brief);
      setBriefEdited(false);
      setRecovery({ kind: "none" });
      rememberInUrl(next.session_id);
      if (next.error) setError(next.error);
    } catch (cause) {
      if (cause instanceof ApiError) {
        setError(cause.advisory);
      } else {
        setError({
          kind: "unexpected",
          message: cause instanceof Error ? cause.message : "Something went wrong.",
          recoverable: true,
        });
      }
    } finally {
      setBusy(null);
    }
  }, []);

  const onStart = useCallback(() => {
    if (!brief) return;
    void guard("Starting the advisory session", () => startSession(brief));
  }, [brief, guard]);

  const onAnswers = useCallback(
    (answers: Record<string, string>, skipped: string[]) => {
      if (!session) return;
      void guard("Sending your answers", () => submitAnswers(session.session_id, answers, skipped));
    },
    [session, guard],
  );

  const onContinue = useCallback(() => {
    if (!session) return;
    void guard("Continuing", () => continueSession(session.session_id));
  }, [session, guard]);

  const onBriefChange = useCallback((next: Brief) => {
    setBrief(next);
    setBriefEdited(true);
  }, []);

  const onStartOver = useCallback(() => {
    const url = new URL(window.location.href);
    url.searchParams.delete("session");
    window.history.replaceState({}, "", url.toString());
    setRecovery({ kind: "none" });
    setSession(null);
    void fetchScenario()
      .then((scenario) => {
        setBrief(scenario.brief);
        setBriefEdited(false);
        setScenarioFailed(false);
      })
      .catch(() => setScenarioFailed(true));
  }, []);

  const advice = session?.recommendation ?? session?.previous_recommendation ?? null;
  const outdated = Boolean(session && !session.recommendation && session.previous_recommendation);
  const roundPending = session?.awaiting_answers ?? false;
  const canContinue = Boolean(session && !roundPending && !session.recommendation && !busy);
  const initiativeCount = brief?.initiatives.length ?? 0;

  return (
    <div className="app">
      <Header connection={connection} organisation={brief?.organisation ?? null} />

      <p className="visually-hidden" role="status" aria-live="polite">
        {busy
          ? `${busy}. The advisor is working. This may take a few minutes.`
          : session?.recommendation
            ? "A recommendation is ready."
            : roundPending
              ? "The advisor has asked some questions."
              : ""}
      </p>

      <RefProvider session={session}>
      <div className="frame">
        <Sidebar
          brief={brief}
          onChange={onBriefChange}
          onStart={onStart}
          busy={busy !== null}
          sessionActive={session !== null}
          briefEdited={briefEdited}
          emptyNote={
            recovery.kind === "missing"
              ? "No brief is loaded. Load the sample brief to begin."
              : recovery.kind === "loading"
                ? "Reopening the session…"
                : scenarioFailed
                  ? "The sample brief could not be loaded. Check the service status above."
                  : "Loading the sample scenario…"
          }
        />

        <main className="main">
          {recovery.kind === "loading" && (
            <p className="notice notice--info">
              <span className="spinner" aria-hidden="true" />
              Reopening session {recovery.id}…
            </p>
          )}

          {recovery.kind === "restored" && (
            <p className="notice notice--info">
              <strong>Reopened.</strong> Session {recovery.id}, as the advisor left it. Nothing was
              regenerated.
            </p>
          )}

          {recovery.kind === "missing" && (
            <div className="notice notice--warn" role="alert">
              <div>
                <strong>Session unavailable.</strong> Session {recovery.id} was not found. Sessions
                are held in the advisor's memory and are lost when it restarts, so this link may
                have outlived it. Nothing has been started.
              </div>
              <button className="button" onClick={onStartOver}>
                Load the sample brief
              </button>
            </div>
          )}

          {error && (
            <div className="notice notice--warn" role="alert">
              <div>
                <strong>
                  {error.recoverable ? "Could not finish that step." : "Something needs attention."}
                </strong>{" "}
                {error.message}
                {error.recoverable && " You can try again."}
                {error.details && error.details.length > 0 && (
                  <details className="disclose">
                    <summary className="disclose__summary">Technical detail</summary>
                    <ul className="disclose__list">
                      {error.details.map((detail, index) => (
                        <li key={index}>{detail}</li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
              <button className="button button--quiet" onClick={() => setError(null)}>
                Dismiss
              </button>
            </div>
          )}

          {!session && (
            <section className="intro">
              <p className="eyebrow">Your decision brief</p>
              <h1 className="h1" tabIndex={-1} ref={headingRef}>
                Start with what you already know.
              </h1>
              <p className="lede">
                {initiativeCount > 0
                  ? `${initiativeCount} candidate initiatives are on the table. The advisor reads the
                     brief, asks only what would change the answer, and sets out the options with
                     their evidence, assumptions and gaps kept apart.`
                  : "The advisor reads your brief, asks only what would change the answer, and sets out the options with their evidence, assumptions and gaps kept apart."}
              </p>
              <p className="muted small">
                Nothing runs until you select <strong>Start advisory session</strong>.
              </p>
            </section>
          )}

          {session && roundPending && (
            <Clarification session={session} busy={busy} onSubmit={onAnswers} />
          )}

          {session && !roundPending && !advice && (
            <section className="intro">
              <p className="eyebrow">Your decision brief</p>
              <h1 className="h1" tabIndex={-1} ref={headingRef}>
                In progress.
              </h1>
              <p className="lede">
                The advisor has paused. Continue when you are ready; nothing runs until you do.
              </p>
              {canContinue && (
                <button className="button button--primary" onClick={onContinue}>
                  Continue
                </button>
              )}
            </section>
          )}

          {session && advice && (
            <>
              <section className="intro">
                <p className="eyebrow">
                  Your decision brief · {advice.items.length} initiative
                  {advice.items.length === 1 ? "" : "s"} considered
                </p>
                <h1 className="h1" tabIndex={-1} ref={headingRef}>
                  A focused place to start.
                </h1>
                {/* The advisor's own summary, in full and at body size. On a
                    narrow screen it folds to a few lines with "Show all". */}
                <p className="lede lede--summary">
                  <ClampText lines={3} narrowOnly>
                    <RefText text={advice.summary} />
                  </ClampText>
                </p>

                {outdated && (
                  <p className="notice notice--warn">
                    <AlertIcon size={15} />
                    <span>
                      <strong>Out of date.</strong> You have answered something since this advice
                      was written, so it no longer reflects what the advisor knows. It is kept for
                      reference. Continue to refresh it.
                    </span>
                  </p>
                )}

                <nav className="tabs" aria-label="Views">
                  <button
                    type="button"
                    className={view === "overview" ? "tab is-active" : "tab"}
                    aria-current={view === "overview"}
                    onClick={() => setView("overview")}
                  >
                    Decision overview
                  </button>
                  <button
                    type="button"
                    className={view === "reasoning" ? "tab is-active" : "tab"}
                    aria-current={view === "reasoning"}
                    onClick={() => setView("reasoning")}
                  >
                    <BookIcon size={14} />
                    Reasoning &amp; sources
                  </button>
                </nav>
              </section>

              {view === "overview" ? (
                <DecisionOverview session={session} onExplain={() => setView("reasoning")} />
              ) : (
                <ReasoningView session={session} />
              )}

              {canContinue && (
                <button className="button" onClick={onContinue}>
                  Continue
                </button>
              )}
            </>
          )}

          {/* Before any advice exists there is still a diagnosis and perhaps a
              comparison worth reading, so the reasoning view is shown directly
              rather than behind a tab that has nothing to switch to. */}
          {session && !advice && !roundPending && <ReasoningView session={session} />}
        </main>
      </div>
      </RefProvider>

      <footer className="foot">
        <span>
          Built for a BlueCallom Enterprise AI Application Developer assessment, using the
          Intelligence-over-Code method.
        </span>
        <span>
          The sample scenario is fictional. Advice is generated and should be checked before
          anything is decided on it.
        </span>
      </footer>
    </div>
  );
}
