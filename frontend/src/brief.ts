import type { Brief } from "./api/client";

/**
 * The brief as a draft, and whether it still matches the advice on screen.
 *
 * The editor works on a copy. Nothing it does reaches the brief until the
 * manager applies it, so cancelling is free. Whether the advice still applies
 * is not a flag someone has to remember to set: it is a comparison between the
 * brief on screen and the brief the session was run on. Applying an unchanged
 * draft therefore changes nothing, and undoing an edit by hand restores the
 * advice as current, because the two briefs are equal again.
 */

/** Serialise with sorted keys, so key order never makes two briefs differ. */
function canonical(value: unknown): string {
  if (Array.isArray(value)) return `[${value.map(canonical).join(",")}]`;
  if (value && typeof value === "object") {
    const entries = Object.keys(value as Record<string, unknown>)
      .sort()
      .map((key) => `${JSON.stringify(key)}:${canonical((value as Record<string, unknown>)[key])}`);
    return `{${entries.join(",")}}`;
  }
  return JSON.stringify(value ?? null);
}

export function sameBrief(a: Brief | null, b: Brief | null): boolean {
  if (a === b) return true;
  if (!a || !b) return false;
  return canonical(a) === canonical(b);
}

/** A deep copy for the editor to change freely. */
export function draftOf(brief: Brief): Brief {
  return JSON.parse(JSON.stringify(brief)) as Brief;
}

/**
 * The brief after the manager applies a draft. An unchanged draft returns the
 * current brief itself, so nothing downstream sees a change.
 */
export function applyDraft(current: Brief, draft: Brief): Brief {
  return sameBrief(current, draft) ? current : draft;
}

/**
 * True when there is a session and the brief on screen is not the one it was
 * run on. Its advice, questions and comparison then belong to another brief.
 */
export function briefDiffersFromSession(
  sessionBrief: Brief | null | undefined,
  brief: Brief | null,
): boolean {
  if (!sessionBrief || !brief) return false;
  return !sameBrief(sessionBrief, brief);
}
