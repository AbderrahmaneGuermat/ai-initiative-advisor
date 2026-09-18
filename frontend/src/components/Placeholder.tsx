/**
 * A labelled empty region.
 *
 * Every placeholder states what will eventually occupy the space and marks
 * itself as not implemented. Nothing in the skeleton shows sample content that
 * could be mistaken for generated advice.
 */
export default function Placeholder({ label, note }: { label: string; note: string }) {
  return (
    <div className="placeholder">
      <div className="placeholder__head">
        <span className="placeholder__label">{label}</span>
        <span className="placeholder__tag">not implemented</span>
      </div>
      <p className="placeholder__note">{note}</p>
    </div>
  );
}
