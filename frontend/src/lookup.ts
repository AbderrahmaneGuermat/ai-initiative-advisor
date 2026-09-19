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
 * Whether the advice establishes that one option comes before the others.
 *
 * It does not. The contract carries a disposition per option and no priority
 * field, and array order is not a claim the model was asked to make, so
 * treating position as rank would be inventing a judgement. Kept as a named
 * function so the reasoning is visible where a future priority field would be
 * read instead.
 */
export function priorityIsExplicit(): boolean {
  return false;
}
