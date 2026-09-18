/**
 * A permanent, unmissable statement of what this build actually is.
 *
 * It stays until the application does something real. An interface that looks
 * finished while doing nothing is the most misleading thing a skeleton can be.
 */
export default function PrototypeBanner() {
  return (
    <div className="banner" role="status">
      <strong className="banner__label">Unfinished prototype</strong>
      <span className="banner__text">
        Layout only. No AI model is connected, no advice is generated, and every panel below is a
        placeholder. Nothing shown here is a real recommendation.
      </span>
    </div>
  );
}
