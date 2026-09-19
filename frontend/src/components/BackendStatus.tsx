import type { ConnectionState } from "../api/client";

/**
 * Whether the advisor is usable, in the manager's terms.
 *
 * **Version and build stage are deliberately absent.** They told a manager
 * nothing and took the most prominent corner of the page to do it. Both remain
 * available at `/api/diagnostics`, which is where developer metadata belongs.
 *
 * What stays here is what changes what a manager can do: whether the backend is
 * reachable, and whether the advisor is configured at all. A configuration
 * problem is reported with the fix, because it is the one failure the manager
 * can act on themselves.
 */
export default function BackendStatus({ connection }: { connection: ConnectionState }) {
  if (connection.kind === "checking") {
    return (
      <div className="status status--checking">
        <span className="status__dot" aria-hidden="true" />
        <span>Checking…</span>
      </div>
    );
  }

  if (connection.kind === "failed") {
    return (
      <div className="status status--failed" role="status">
        <span className="status__dot" aria-hidden="true" />
        <div className="status__body">
          <span className="status__headline">Not connected</span>
          <span className="status__detail">
            The advisor service is not responding. Start it with <code>npm run dev</code>.
          </span>
        </div>
      </div>
    );
  }

  const { health } = connection;

  if (!health.model_configured_locally) {
    return (
      <div className="status status--failed" role="status">
        <span className="status__dot" aria-hidden="true" />
        <div className="status__body">
          <span className="status__headline">Advisor not configured</span>
          <span className="status__detail">
            {health.configuration_problems[0] ?? "No model provider is set up."}
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="status status--connected">
      <span className="status__dot" aria-hidden="true" />
      <div className="status__body">
        <span className="status__headline">Ready</span>
        <span className="status__detail">Credentials are checked on the first request.</span>
      </div>
    </div>
  );
}
