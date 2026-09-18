import { useCallback, useEffect, useState } from "react";

import {
  ApiError,
  continueSession,
  fetchHealth,
  fetchScenario,
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

/**
 * Application shell.
 *
 * Holds the brief being edited and the current session. Everything advisory
 * comes from the backend; nothing here decides anything about the advice.
 *
 * Editing the brief after a session has started begins a **new** session rather
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

    fetchScenario()
      .then((scenario) => setBrief(scenario.brief))
      .catch(() => {
        /* The status indicator already reports an unreachable backend. */
      });

    return () => controller.abort();
  }, []);

  const guard = useCallback(async (label: string, work: () => Promise<SessionView>) => {
    setBusy(label);
    setError(null);
    try {
      const next = await work();
      setSession(next);
      setBriefEdited(false);
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

      {error && <ErrorNotice error={error} onDismiss={() => setError(null)} />}

      <main className="app__main">
        <ContextPanel
          brief={brief}
          onChange={onBriefChange}
          onStart={onStart}
          busy={busy !== null}
          sessionActive={session !== null}
          briefEdited={briefEdited}
        />
        <AdvisoryThread
          session={session}
          busy={busy}
          onSubmitAnswers={onAnswers}
          onContinue={onContinue}
        />
        <AdvicePanel session={session} />
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
