import { createContext, useContext, useMemo, type ReactNode } from "react";

import type { SessionView } from "../api/client";
import { referenceIndex, splitReferences, type InlineRef } from "../lookup";

/**
 * Model prose with its identifiers made readable.
 *
 * "(Q-HISTDATA)" becomes "your answer", "OBJ-LATE" becomes the objective it
 * names. The stored text is not changed: this only decides how each exact,
 * resolvable identifier is drawn. The identifier stays on the element as
 * `data-ref` and in its accessible description, and every source a
 * recommendation cites is listed with its identifier under "Evidence & sources"
 * and in the reasoning view. Anything that does not resolve is printed as
 * written.
 */

const RefIndex = createContext<Map<string, InlineRef>>(new Map());

export function RefProvider({
  session,
  children,
}: {
  session: SessionView | null;
  children: ReactNode;
}) {
  const index = useMemo(() => referenceIndex(session), [session]);
  return <RefIndex.Provider value={index}>{children}</RefIndex.Provider>;
}

export default function RefText({ text }: { text: string }) {
  const index = useContext(RefIndex);
  const segments = useMemo(() => splitReferences(text, index), [text, index]);

  return (
    <>
      {segments.map((segment, i) =>
        "text" in segment ? (
          <span key={i}>{segment.text}</span>
        ) : (
          <span
            key={i}
            className="ref-inline"
            data-ref={segment.ref.id}
            title={`${segment.ref.kind} ${segment.ref.id}: ${segment.ref.detail}`}
          >
            {segment.ref.label}
          </span>
        ),
      )}
    </>
  );
}
