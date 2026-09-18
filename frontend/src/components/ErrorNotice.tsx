import type { AdvisoryError } from "../api/client";

/**
 * A failure, stated plainly.
 *
 * Never replaced with sample content and never hidden. If the advisor could not
 * complete a step, the manager is told, and whatever advice already existed
 * stays exactly as it was.
 *
 * Technical detail is kept out of the manager's way: the message is written for
 * them, and the underlying validation errors are available behind a disclosure
 * for whoever is debugging.
 */
export default function ErrorNotice({
  error,
  onDismiss,
}: {
  error: AdvisoryError;
  onDismiss: () => void;
}) {
  return (
    <div className="banner banner--error" role="alert">
      <div className="banner__body">
        <strong className="banner__label">
          {error.recoverable ? "Could not finish that step" : "Something needs attention"}
        </strong>
        <span className="banner__text">{error.message}</span>
        {error.recoverable && (
          <span className="banner__text muted small">You can try again.</span>
        )}
        {error.details && error.details.length > 0 && (
          <details className="banner__details">
            <summary>Technical detail</summary>
            <ul className="list">
              {error.details.map((detail, index) => (
                <li key={index}>{detail}</li>
              ))}
            </ul>
          </details>
        )}
      </div>
      <button className="button button--quiet" onClick={onDismiss}>
        Dismiss
      </button>
    </div>
  );
}
