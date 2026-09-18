import type { ConnectionState } from "../api/client";

/**
 * Shows whether the frontend can reach the backend.
 *
 * This is the one genuinely functional element in the skeleton. It exists so
 * that a developer can confirm the proxy and the backend are working without
 * opening a terminal or the network tab.
 */
export default function BackendStatus({ connection }: { connection: ConnectionState }) {
  if (connection.kind === "checking") {
    return (
      <div className="status status--checking">
        <span className="status__dot" aria-hidden="true" />
        <span>Checking backend…</span>
      </div>
    );
  }

  if (connection.kind === "failed") {
    return (
      <div className="status status--failed">
        <span className="status__dot" aria-hidden="true" />
        <div className="status__body">
          <span className="status__headline">Backend unreachable</span>
          <span className="status__detail">{connection.message}</span>
          <span className="status__detail">
            Start both processes with <code>npm run dev</code> from the repository root.
          </span>
        </div>
      </div>
    );
  }

  const { health } = connection;

  return (
    <div className="status status--connected">
      <span className="status__dot" aria-hidden="true" />
      <div className="status__body">
        <span className="status__headline">
          Backend connected · v{health.version} · stage: {health.stage}
        </span>
        <span className="status__detail">
          {health.model_configured
            ? "Advisor ready"
            : "No model configured. Advisory steps will not run until MODEL_API_KEY is set."}
        </span>
      </div>
    </div>
  );
}
