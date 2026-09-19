import type { SessionView, SourceRef, Stance } from "./api/client";

/**
 * Turning identifiers into something a manager can read.
 *
 * The backend speaks in identifiers because they have to resolve exactly.
 * `INI-ROUTE` and `Q-HISTDATA` are correct and unreadable, so the interface
 * shows the initiative's name or the question's text instead.
 *
 * **The identifier is never thrown away.** Every readable label carries its
 * original reference alongside, so a reader checking provenance can still see
 * precisely what was cited. Where no mapping exists the identifier is shown as
 * it is, rather than guessed at or hidden.
 */

export const STANCE_LABEL: Record<Stance, string> = {
  recommended: "Recommended",
  consider_later: "Consider later",
  not_recommended: "Not recommended",
  insufficient_information: "Not enough information",
};

export type Readable = {
  /** What to show. Falls back to the raw identifier when nothing maps. */
  label: string;
  /** The identifier itself, always available. */
  id: string;
  /** What kind of thing it is, in the manager's terms. */
  kind: string;
  /** True when a real mapping was found. */
  resolved: boolean;
};

export function initiativeName(session: SessionView | null, id: string): string {
  return session?.brief.initiatives.find((i) => i.id === id)?.name ?? id;
}

export function questionText(session: SessionView | null, id: string): string | null {
  return session?.questions.find((q) => q.id === id)?.question ?? null;
}

/** A source reference, rendered for a person while keeping its identifier. */
export function readableSource(session: SessionView | null, ref: SourceRef): Readable {
  const brief = session?.brief;

  if (ref.kind === "brief.objective") {
    const found = brief?.objectives.find((o) => o.id === ref.ref_id);
    return {
      label: found?.statement ?? ref.ref_id,
      id: ref.ref_id,
      kind: "Objective",
      resolved: Boolean(found),
    };
  }

  if (ref.kind === "brief.constraint") {
    const found = brief?.constraints.find((c) => c.id === ref.ref_id);
    return {
      label: found ? found.kind : ref.ref_id,
      id: ref.ref_id,
      kind: "Constraint",
      resolved: Boolean(found),
    };
  }

  if (ref.kind === "brief.initiative") {
    const found = brief?.initiatives.find((i) => i.id === ref.ref_id);
    return {
      label: found?.name ?? ref.ref_id,
      id: ref.ref_id,
      kind: "Option",
      resolved: Boolean(found),
    };
  }

  if (ref.kind === "clarification.answer") {
    const text = questionText(session, ref.ref_id);
    return {
      label: text ?? ref.ref_id,
      id: ref.ref_id,
      kind: "Your answer",
      resolved: Boolean(text),
    };
  }

  return { label: ref.ref_id, id: ref.ref_id, kind: ref.kind, resolved: false };
}

/**
 * Identifiers the model wrote into prose, such as "(Q-HISTDATA)" or "address
 * OBJ-LATE". Only the exact identifiers this session holds are replaced; a
 * token that merely looks like one is left exactly as written.
 */
const ID_PATTERN = /\b[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+\b/g;

export type InlineRef = { id: string; label: string; kind: string; detail: string };

export type Segment = { text: string } | { ref: InlineRef };

/** Every identifier the session can resolve, with how to show it inline. */
export function referenceIndex(session: SessionView | null): Map<string, InlineRef> {
  const index = new Map<string, InlineRef>();
  if (!session) return index;
  const { brief } = session;

  for (const o of brief.objectives) {
    index.set(o.id, { id: o.id, label: o.statement, kind: "Objective", detail: o.statement });
  }
  for (const c of brief.constraints) {
    index.set(c.id, {
      id: c.id,
      label: `${c.kind} constraint`,
      kind: "Constraint",
      detail: c.value ?? "Not stated",
    });
  }
  for (const i of brief.initiatives) {
    index.set(i.id, { id: i.id, label: i.name, kind: "Option", detail: i.name });
  }
  for (const q of session.questions) {
    // An answered question is cited for what the manager said. An open one is
    // named by its own opening words, because a generic label reads badly in
    // the model's sentences ("relates to unanswered ..."). The full question
    // is in the tooltip and is listed in full under "Confirm before committing".
    const label = q.status === "answered" ? "your answer" : `“${opening(q.question)}”`;
    index.set(q.id, { id: q.id, label, kind: "Question", detail: q.question });
  }
  return index;
}

/** The first few words of a question, marked as cut when it is. */
export function opening(text: string, words = 6): string {
  const parts = text.trim().split(/\s+/);
  return parts.length <= words ? parts.join(" ") : `${parts.slice(0, words).join(" ")}…`;
}

/**
 * Split prose into plain text and resolved references. Joining the pieces back
 * with each reference's `id` reproduces the original text exactly, which is
 * what keeps this a presentation change rather than an edit of model output.
 */
export function splitReferences(text: string, index: Map<string, InlineRef>): Segment[] {
  const segments: Segment[] = [];
  let last = 0;
  for (const match of text.matchAll(ID_PATTERN)) {
    const ref = index.get(match[0]);
    if (!ref) continue;
    const start = match.index ?? 0;
    if (start > last) segments.push({ text: text.slice(last, start) });
    segments.push({ ref });
    last = start + match[0].length;
  }
  if (last < text.length) segments.push({ text: text.slice(last) });
  return segments;
}

/**
 * Whether the interface labels one option as coming before the others.
 *
 * It does not. The recommend prompt and the backend contract say list order
 * carries priority, and the interface keeps that order within each group. But
 * nothing validates the order, and there is no field that states it, so the
 * interface does not turn position into a "Recommended first" label. See
 * docs/decisions.md, D-048, which corrects the rationale first given in D-045.
 */
export function priorityIsExplicit(): boolean {
  return false;
}
