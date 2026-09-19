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
import BackendStatus from "./components/BackendStatus";
import ContextPanel from "./components/ContextPanel";
import AdvisoryThread from "./components/AdvisoryThread";
import AdvicePanel from "./components/AdvicePanel";
import ErrorNotice from "./components/ErrorNotice";
import "./styles/layout.css";

/** The session identifier in the URL, if the page was opened with one. */
function sessionFromUrl(): string | null {
  const value = new URLSearchParams(window.location.search).get("session");
  return value && value.trim() ? value.trim() : null;
}

/** Put a session identifier in the URL without adding a history entry. */
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

/**
 * Application shell.
 *
 * Holds the brief being edited and the current session. Everything advisory
 * comes from the backend; nothing here decides anything about the advice.
 *
 * **Reopening a session.** Opening the page with `?session=<id>` fetches that
 * session and restores what it holds. A session the browser created also puts
 * its identifier in the URL, so a refresh or a reopened tab finds it again.
 *
 * This recovers state the running backend still has in memory. It is **not**
 * persistence: a backend restart loses every session, and the link then reports
 * the session as unavailable rather than pretending otherwise.
 *
 * Recovery is read-only. It issues one GET and never starts a session, submits
 * answers or continues one, so reopening a link costs nothing.
 *
 * Editing the brief after a session has started begins a new session rather
 * than revising the existing one. Revision is not implemented, and presenting
 * fresh advice as a considered change of mind would misrepresent what happened.
 */
export default function App() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "checking" });
  const [brief, setBrief] = useState<Brief | null>(null);
  const [session, setSession] = useState<SessionView | null>(null);
  const [briefEdited, setBriefEdited] = useState(false);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<AdvisoryError | null>(null);
  const [recovery, setRecovery] = useState<Recovery>(() => {
    const id = sessionFromUrl();
    return id ? { kind: "loading", id } : { kind: "none" };
  });

  const adviceRef = useRef<HTMLElement>(null);
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
      // A restored brief must not be overwritten by the sample scenario, so the
      // scenario is not requested at all on this path.
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
      .catch(() => {
        /* The status indicator already reports an unreachable backend. */
      });

    return () => controller.abort();
  }, []);

  const goToAdvice = useCallback(() => {
    const node = adviceRef.current;
    if (!node) return;
    node.scrollIntoView({ behavior: "smooth", block: "start" });
    node.querySelector<HTMLElement>("#advice-heading")?.focus();
  }, []);

  // When a recommendation appears, move focus to it. The manager's attention is
  // wherever they last acted, which is rarely where the answer landed.
  useEffect(() => {
    const has = Boolean(session?.recommendation);
    if (has && !hadRecommendation.current && busy === null) {
      goToAdvice();
    }
    hadRecommendation.current = has;
  }, [session?.recommendation, busy, goToAdvice]);

  const guard = useCallback(async (label: string, work: () => Promise<SessionView>) => {
    setBusy(label);
    setError(null);
    try {
      const next = await work();
      setSession(next);
      setBrief(next.brief);
      setBriefEdited(false);
      setRecovery({ kind: "none" });
      // So a refresh or a reopened tab can find this session again, for as long
      // as the backend still holds it.
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

  /** Load the sample scenario after a failed recovery. A GET, nothing else. */
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
      })
      .catch(() => {
        /* The status indicator already reports an unreachable backend. */
      });
  }, []);

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__identity">
          <h1 className="app__title">AI Initiative Advisor</h1>
          <p className="app__subtitle">
            Prioritise enterprise AI initiatives against your objectives and constraints
          </p>
        </div>
        <BackendStatus connection={connection} />
      </header>

      {recovery.kind === "loading" && (
        <div className="banner banner--info" role="status">
          <span className="spinner" aria-hidden="true" />
          <span className="banner__text">Reopening session {recovery.id}…</span>
        </div>
      )}

      {recovery.kind === "restored" && (
        <div className="banner banner--info" role="status">
          <strong className="banner__label">Reopened</strong>
          <span className="banner__text">
            Session {recovery.id}, as the advisor left it. Nothing was regenerated.
          </span>
        </div>
      )}

      {recovery.kind === "missing" && (
        <div className="banner banner--error" role="alert">
          <div className="banner__body">
            <strong className="banner__label">Session unavailable</strong>
            <span className="banner__text">
              Session {recovery.id} was not found. Sessions are held in the advisor's memory and
              are lost when it restarts, so this link may have outlived it.
            </span>
            <span className="banner__text muted small">
              Nothing has been started. Choosing below loads the sample brief; the advisor only
              runs when you select <em>Start advisory session</em>.
            </span>
          </div>
          <button className="button" onClick={onStartOver}>
            Load the sample brief
          </button>
        </div>
      )}

      {error && <ErrorNotice error={error} onDismiss={() => setError(null)} />}

      <main className="app__main">
        <div className="app__side">
          <ContextPanel
            brief={brief}
            onChange={onBriefChange}
            onStart={onStart}
            busy={busy !== null}
            sessionActive={session !== null}
            briefEdited={briefEdited}
          />
        </div>

        {/* Advice first, then the working detail. On a laptop the two stack in
            one wide column rather than being squeezed into narrow ones. */}
        <div className="app__main-column">
          <AdvicePanel session={session} ref={adviceRef} />
          <AdvisoryThread
            session={session}
            busy={busy}
            onSubmitAnswers={onAnswers}
            onContinue={onContinue}
            onGoToAdvice={goToAdvice}
          />
        </div>
      </main>

      <footer className="app__footer">
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
