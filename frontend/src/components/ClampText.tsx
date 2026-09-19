import { useEffect, useLayoutEffect, useRef, useState, type CSSProperties, type ReactNode } from "react";

/**
 * Content shown in a few lines, with an explicit control to read the rest.
 *
 * The control appears only when the content is actually cut, and it is a real
 * button: reachable by keyboard, usable by touch, announced with its state.
 * A tooltip is never the only way to read what was clipped.
 *
 * `narrowOnly` clamps on narrow screens only; on a wide screen the content is
 * shown in full and no control appears.
 */
export default function ClampText({
  children,
  lines = 3,
  narrowOnly = false,
}: {
  children: ReactNode;
  lines?: number;
  narrowOnly?: boolean;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const [open, setOpen] = useState(false);
  const [clipped, setClipped] = useState(false);

  const measure = () => {
    const node = ref.current;
    if (!node || open) return;
    setClipped(node.scrollHeight > node.clientHeight + 1);
  };

  useLayoutEffect(measure, [children, open]);

  // Measure again whenever the box changes size, including when a hidden
  // ancestor is shown: text measured while hidden looks uncut, and the
  // "Show all" control would never appear.
  useEffect(() => {
    const node = ref.current;
    if (!node || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(() => measure());
    observer.observe(node);
    return () => observer.disconnect();
  });

  const classes = open ? "" : narrowOnly ? "clamp clamp--narrow" : "clamp";

  return (
    <>
      <span
        ref={ref}
        className={classes || undefined}
        style={open ? undefined : ({ "--clamp-lines": lines } as CSSProperties)}
      >
        {children}
      </span>
      {(clipped || open) && (
        <button
          type="button"
          className="more-toggle"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          {open ? "Show less" : "Show all"}
        </button>
      )}
    </>
  );
}
