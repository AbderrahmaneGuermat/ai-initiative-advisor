import { useEffect, useState } from "react";

import { fetchHealth, type ConnectionState } from "./api/client";
import PrototypeBanner from "./components/PrototypeBanner";
import BackendStatus from "./components/BackendStatus";
import ContextPanel from "./components/ContextPanel";
import AdvisoryThread from "./components/AdvisoryThread";
import AdvicePanel from "./components/AdvicePanel";
import "./styles/layout.css";

/**
 * Application shell.
 *
 * Skeleton stage. This renders the proposed three-region layout so the
 * structure can be reviewed, and verifies that the frontend can reach the
 * backend. None of the advisory behaviour exists yet, and every panel says so
 * rather than showing invented content.
 */
export default function App() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "checking" });

  useEffect(() => {
    const controller = new AbortController();

    fetchHealth(controller.signal)
      .then((health) => setConnection({ kind: "connected", health }))
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setConnection({
          kind: "failed",
          message: error instanceof Error ? error.message : "Unknown error",
        });
      });

    return () => controller.abort();
  }, []);

  return (
    <div className="app">
      <PrototypeBanner />

      <header className="app__header">
        <div className="app__identity">
          <h1 className="app__title">AI Initiative Advisor</h1>
          <p className="app__subtitle">
            Prioritise enterprise AI initiatives against your objectives and constraints
          </p>
        </div>
        <BackendStatus connection={connection} />
      </header>

      <main className="app__main">
        <ContextPanel />
        <AdvisoryThread />
        <AdvicePanel />
      </main>

      <footer className="app__footer">
        <span>
          Built for a BlueCallom Enterprise AI Application Developer assessment, using the
          Intelligence-over-Code method.
        </span>
        <span>
          All demonstration data is fictional. See <code>docs/</code> for requirements,
          architecture and decisions.
        </span>
      </footer>
    </div>
  );
}
