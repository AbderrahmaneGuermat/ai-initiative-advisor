import { useCallback, useEffect, useRef, useState } from "react";

import {
  ApiError,
  continueSession,
  fetchHealth,
  fetchScenario,
  fetchSession,
  startSession,
  submitAnswers,
  type AdvisoryError,
  type Brief,
  type ConnectionState,
  type SessionView,
} from "./api/client";
import { applyDraft, briefDiffersFromSession } from "./brief";
import Header from "./components/Header";
import Sidebar from "./components/Sidebar";
import BriefEditor from "./components/BriefEditor";
import Clarification from "./components/Clarification";
import DecisionOverview from "./components/DecisionOverview";
import ReasoningView from "./components/ReasoningView";
import ClampText from "./components/ClampText";
import RefText, { RefProvider } from "./components/RefText";
import { AlertIcon, BookIcon, CheckIcon } from "./components/icons";
import "./styles/layout.css";

function sessionFromUrl(): string | null {
  const value = new URLSearchParams(window.location.search).get("session");
  return value && value.trim() ? value.trim() : null;
}

function rememberInUrl(sessionId: string): void {
  const url = new URL(window.location.href);
  if (url.searchParams.get("session") === sessionId) return;
  url.searchParams.set("session", sessionId);
  window.history.replaceState({}, "", url.toString());
}

function sessionLink(sessionId: string): string {
  const url = new URL(window.location.href);
  url.searchParams.set("session", sessionId);
  return url.toString();
}

type Recovery =
  | { kind: "none" }
  | { kind: "loading"; id: string }
  | { kind: "restored"; id: string }
  | { kind: "missing"; id: string };

type View = "overview" | "reasoning";

const EDITOR_ID = "brief-editor";

/**
 * Application shell.
 *
 * Layout: a compact context sidebar and one main column. The main column shows
 * whatever the session most needs attention on. While a clarification round is
 * open, the form is the first thing in it.
 *
 * **Editing the brief.** The editor opens in the main column and works on a
 * draft. Cancel discards it. Apply replaces the brief only if something
 * changed. Whether the advice on screen still applies is a comparison, not a
 * flag: if the brief differs from the one the session was run on, the old
 * advice and questions are withdrawn from view (kept mounted, so unsent
 * answers survive) and the manager is told a new advisory session is needed.
 * Starting it is a separate click. Nothing in the editor calls the backend.
 *
 * **Reopening a session.** `?session=<id>` fetches that session and restores it.
 * A session created here writes its identifier into the URL. This recovers
 * in-memory backend state; it is not persistence, and a backend restart loses
 * every session. Recovery issues one GET and never runs the advisor.
 */
export default function App() {
  const [connection, setConnection] = useState<ConnectionState>({ kind: "checking" });
  const [brief, setBrief] = useState<Brief | null>(null);
  const [session, setSession] = useState<SessionView | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<AdvisoryError | null>(null);
  const [view, setView] = useState<View>("overview");
  const [editing, setEditing] = useState(false);
  const [scenarioFailed, setScenarioFailed] = useState(false);
  const [recovery, setRecovery] = useState<Recovery>(() => {
    const id = sessionFromUrl();
    return id ? { kind: "loading", id } : { kind: "none" };
  });

  const headingRef = useRef<HTMLHeadingElement>(null);
  const changedRef = useRef<HTMLHeadingElement>(null);
  const hadRecommendation = useRef(false);
  const returnFocus = useRef<HTMLElement | null>(null);
  const focusAfterEdit = useRef<"return" | "changed" | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetchHealth(controller.signal)
      .then((health) => setConnection({ kind: "connected", health }))
      .catch((cause: unknown) => {
        if (cause instanceof DOMException && cause.name === "AbortError") return;
        setConnection({
          kind: "failed",
          message: cause instanceof Error ? cause.message : "Unknown error",
        });
      });

    const requested = sessionFromUrl();

    if (requested) {
      // The sample scenario is not requested on this path, so it cannot
      // overwrite a restored brief.
      fetchSession(requested)
        .then((restored) => {
          setSession(restored);
          setBrief(restored.brief);
          setRecovery({ kind: "restored", id: requested });
          if (restored.error) setError(restored.error);
        })
        .catch(() => setRecovery({ kind: "missing", id: requested }));
      return () => controller.abort();
    }

    fetchScenario()
      .then((scenario) => setBrief(scenario.brief))
      .catch(() => setScenarioFailed(true));

    return () => controller.abort();
  }, []);

  // When advice arrives, move focus to the brief's heading. Attention is
  // wherever the manager last acted, which is rarely where the answer landed.
  useEffect(() => {
    const has = Boolean(session?.recommendation);
    if (has && !hadRecommendation.current && busy === null) {
      setView("overview");
      headingRef.current?.focus();
    }
    hadRecommendation.current = has;
  }, [session?.recommendation, busy]);

  // After the editor closes, focus goes where the manager can carry on: to the
  // "brief changed" heading if the change withdrew the advice, otherwise back
  // to the control that opened the editor.
  useEffect(() => {
    if (editing || focusAfterEdit.current === null) return;
    const target = focusAfterEdit.current;
    focusAfterEdit.current = null;
    if (target === "changed" && changedRef.current) {
      changedRef.current.focus();
      return;
    }
    const back = returnFocus.current;
    if (back && back.isConnected) back.focus();
    else headingRef.current?.focus();
  }, [editing]);

  const guard = useCallback(async (label: string, work: () => Promise<SessionView>) => {
    setBusy(label);
    setError(null);
    try {
      const next = await work();
      setSession(next);
      setBrief(next.brief);
      setRecovery({ kind: "none" });
      rememberInUrl(next.session_id);
      if (next.error) setError(next.error);
    } catch (cause) {
      if (cause instanceof ApiError) {
        setError(cause.advisory);
      } else {
        setError({
          kind: "unexpected",
          message: cause instanceof Error ? cause.message : "Something went wrong.",
          recoverable: true,
        });
      }
    } finally {
      setBusy(null);
    }
  }, []);

  const onStart = useCallback(() => {
    if (!brief || editing) return;
    setView("overview");
    void guard("Starting the advisory session", () => startSession(brief));
  }, [brief, editing, guard]);

  const onAnswers = useCallback(
    (answers: Record<string, string>, skipped: string[]) => {
      if (!session) return;
      void guard("Sending your answers", () => submitAnswers(session.session_id, answers, skipped));
    },
    [session, guard],
  );

  const onContinue = useCallback(() => {
    if (!session) return;
    void guard("Continuing", () => continueSession(session.session_id));
  }, [session, guard]);

  const openEditor = useCallback(() => {
    if (editing) {
      focusAfterEdit.current = "return";
      setEditing(false);
      return;
    }
    returnFocus.current = document.activeElement as HTMLElement | null;
    setEditing(true);
    window.scrollTo({ top: 0 });
  }, [editing]);

  const onCancelEdit = useCallback(() => {
    focusAfterEdit.current = "return";
    setEditing(false);
  }, []);

  const onApplyEdit = useCallback(
    (draft: Brief) => {
      if (!brief) return;
      const next = applyDraft(brief, draft);
      const withdrawsAdvice = Boolean(session) && briefDiffersFromSession(session?.brief, next);
      if (next !== brief) setBrief(next);
      focusAfterEdit.current = withdrawsAdvice ? "changed" : "return";
      setEditing(false);
      window.scrollTo({ top: 0 });
    },
    [brief, session],
  );

  const onDiscardChanges = useCallback(() => {
    if (!session) return;
    setBrief(session.brief);
    window.requestAnimationFrame(() => headingRef.current?.focus());
  }, [session]);

  const onStartOver = useCallback(() => {
    const url = new URL(window.location.href);
    url.searchParams.delete("session");
    window.history.replaceState({}, "", url.toString());
    setRecovery({ kind: "none" });
    setSession(null);
    void fetchScenario()
      .then((scenario) => {
        setBrief(scenario.brief);
        setScenarioFailed(false);
      })
      .catch(() => setScenarioFailed(true));
  }, []);

  const briefChanged = briefDiffersFromSession(session?.brief, brief);
  const advice = session?.recommendation ?? session?.previous_recommendation ?? null;
  const outdated = Boolean(session && !session.recommendation && session.previous_recommendation);
  const roundPending = session?.awaiting_answers ?? false;
  const canContinue = Boolean(session && !roundPending && !session.recommendation && !busy);
  const initiativeCount = brief?.initiatives.length ?? 0;

  return (
    <div className="app">
      <Header connection={connection} organisation={brief?.organisation ?? null} />

      <p className="visually-hidden" role="status" aria-live="polite">
        {busy
          ? `${busy}. The advisor is working. This may take a few minutes.`
          : briefChanged
            ? "Your brief has changed. A new advisory session is needed."
            : session?.recommendation
              ? "A recommendation is ready."
              : roundPending
                ? "The advisor has asked some questions."
                : ""}
      </p>

      <RefProvider session={session}>
        <div className="frame">
          <Sidebar
            brief={brief}
            onStart={onStart}
            onEdit={openEditor}
            editing={editing}
            editorId={EDITOR_ID}
            busy={busy !== null}
            sessionActive={session !== null}
            briefEdited={briefChanged}
            emptyNote={
              recovery.kind === "missing"
                ? "No brief is loaded. Load the sample brief to begin."
                : recovery.kind === "loading"
                  ? "Reopening the session…"
                  : scenarioFailed
                    ? "The sample brief could not be loaded. Check the service status above."
                    : "Loading the sample scenario…"
            }
          />

          <main className="main">
            {recovery.kind === "loading" && (
              <p className="notice notice--info">
                <span className="spinner" aria-hidden="true" />
                Reopening the session…
              </p>
            )}

            {recovery.kind === "missing" && (
              <div className="notice notice--warn" role="alert">
                <div>
                  <strong>Session unavailable.</strong> Session {recovery.id} was not found.
                  Sessions are held in the advisor's memory and are lost when it restarts, so this
                  link may have outlived it. Nothing has been started.
                </div>
                <button className="button" onClick={onStartOver}>
                  Load the sample brief
                </button>
              </div>
            )}

            {error && (
              <div className="notice notice--warn" role="alert">
                <div>
                  <strong>
                    {error.recoverable
                      ? "Could not finish that step."
                      : "Something needs attention."}
                  </strong>{" "}
                  {error.message}
                  {error.recoverable && " You can try again."}
                  {error.details && error.details.length > 0 && (
                    <details className="disclose">
                      <summary className="disclose__summary">Technical detail</summary>
                      <ul className="disclose__list">
                        {error.details.map((detail, index) => (
                          <li key={index}>{detail}</li>
                        ))}
                      </ul>
                    </details>
                  )}
                </div>
                <button className="button button--quiet" onClick={() => setError(null)}>
                  Dismiss
                </button>
              </div>
            )}

            {editing && brief && (
              <div id={EDITOR_ID}>
                <BriefEditor
                  brief={brief}
                  sessionActive={session !== null}
                  onApply={onApplyEdit}
                  onCancel={onCancelEdit}
                />
              </div>
            )}

            {/* Everything else stays mounted while the editor is open, so a
                half-written answer to a pending question is still there when
                the manager comes back. */}
            <div className="main__stack" hidden={editing}>
              {recovery.kind === "restored" && session && !briefChanged && (
                <div className="restored">
                  <span className="restored__status">
                    <CheckIcon size={13} />
                    Session restored
                  </span>
                  <details className="restored__details">
                    <summary>What this means</summary>
                    <p>
                      Existing results were loaded as the advisor left them. Nothing was
                      regenerated and the advisor was not asked anything. Sessions are held in the
                      advisor's memory and are lost if it restarts. Session{" "}
                      <code>{recovery.id}</code>.
                    </p>
                  </details>
                </div>
              )}

              {briefChanged && session && (
                <section className="changed" aria-labelledby="changed-heading">
                  <p className="eyebrow">Your decision brief</p>
                  <h1 className="h1" id="changed-heading" tabIndex={-1} ref={changedRef}>
                    Your brief has changed.
                  </h1>
                  <p className="lede">
                    The advice and questions you had were produced for the brief as it was, so they
                    are not shown for this one. Start a new advisory session to get advice for the
                    changed brief. Nothing starts until you do.
                  </p>
                  <div className="changed__actions">
                    <button
                      type="button"
                      className="button button--primary"
                      onClick={onStart}
                      disabled={busy !== null}
                    >
                      {busy ? "Working…" : "Start a new advisory session"}
                    </button>
                    <button type="button" className="text-link" onClick={onDiscardChanges}>
                      Discard the changes and return to the previous advice
                    </button>
                  </div>
                  <p className="muted small">
                    The previous session keeps its own link while the advisor is running:{" "}
                    <a className="inline-link" href={sessionLink(session.session_id)}>
                      reopen the previous session
                    </a>
                    . Opening it loads that session's brief, not your changes.
                  </p>
                </section>
              )}

              <div className="main__stack" hidden={briefChanged}>
                {!session && (
                  <section className="intro">
                    <p className="eyebrow">Your decision brief</p>
                    <h1 className="h1" tabIndex={-1} ref={headingRef}>
                      Start with what you already know.
                    </h1>
                    <p className="lede">
                      {initiativeCount > 0
                        ? `${initiativeCount} candidate initiatives are on the table. The advisor reads the
                     brief, asks only what would change the answer, and sets out the options with
                     their evidence, assumptions and gaps kept apart.`
                        : "The advisor reads your brief, asks only what would change the answer, and sets out the options with their evidence, assumptions and gaps kept apart."}
                    </p>
                    <p className="muted small">
                      Nothing runs until you select <strong>Start advisory session</strong>.
                    </p>
                  </section>
                )}

                {session && roundPending && (
                  <Clarification session={session} busy={busy} onSubmit={onAnswers} />
                )}

                {session && !roundPending && !advice && (
                  <section className="intro">
                    <p className="eyebrow">Your decision brief</p>
                    <h1 className="h1" tabIndex={-1} ref={headingRef}>
                      In progress.
                    </h1>
                    <p className="lede">
                      The advisor has paused. Continue when you are ready; nothing runs until you
                      do.
                    </p>
                    {canContinue && (
                      <button className="button button--primary" onClick={onContinue}>
                        Continue
                      </button>
                    )}
                  </section>
                )}

                {session && advice && (
                  <>
                    <section className="intro">
                      <p className="eyebrow">
                        Your decision brief · {advice.items.length} initiative
                        {advice.items.length === 1 ? "" : "s"} considered
                      </p>
                      <h1 className="h1" tabIndex={-1} ref={headingRef}>
                        A focused place to start.
                      </h1>
                      {/* The advisor's own summary, in full and at body size. On a
                          narrow screen it folds to a few lines with "Show all". */}
                      <p className="lede lede--summary">
                        <ClampText lines={3} narrowOnly>
                          <RefText text={advice.summary} />
                        </ClampText>
                      </p>

                      {outdated && (
                        <p className="notice notice--warn">
                          <AlertIcon size={15} />
                          <span>
                            <strong>Out of date.</strong> You have answered something since this
                            advice was written, so it no longer reflects what the advisor knows. It
                            is kept for reference. Continue to refresh it.
                          </span>
                        </p>
                      )}

                      <nav className="tabs" aria-label="Views">
                        <button
                          type="button"
                          className={view === "overview" ? "tab is-active" : "tab"}
                          aria-current={view === "overview"}
                          onClick={() => setView("overview")}
                        >
                          Decision overview
                        </button>
                        <button
                          type="button"
                          className={view === "reasoning" ? "tab is-active" : "tab"}
                          aria-current={view === "reasoning"}
                          onClick={() => setView("reasoning")}
                        >
                          <BookIcon size={14} />
                          Reasoning &amp; sources
                        </button>
                      </nav>
                    </section>

                    {view === "overview" ? (
                      <DecisionOverview session={session} onExplain={() => setView("reasoning")} />
                    ) : (
                      <ReasoningView session={session} />
                    )}

                    {canContinue && (
                      <button className="button" onClick={onContinue}>
                        Continue
                      </button>
                    )}
                  </>
                )}

                {/* Before any advice exists there is still a diagnosis and perhaps a
                    comparison worth reading, so the reasoning view is shown directly
                    rather than behind a tab that has nothing to switch to. */}
                {session && !advice && !roundPending && <ReasoningView session={session} />}
              </div>
            </div>
          </main>
        </div>
      </RefProvider>

      <footer className="foot">
        <span>
          Built for a BlueCallom Enterprise AI Application Developer assessment, using the
          Intelligence-over-Code method.
        </span>
        <span>
          The sample scenario is fictional. Advice is generated and should be checked before
          anything is decided on it.
        </span>
      </footer>
    </div>
  );
}
