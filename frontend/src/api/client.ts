/**
 * Backend API client.
 *
 * Every request goes through /api, which the dev server proxies to the backend.
 * No model provider is ever called from the browser and no API key reaches this
 * code. Provider details are not part of the manager's workflow; they live on
 * the diagnostics endpoint, which this interface does not display.
 */

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  stage: string;
  /**
   * Whether usable configuration is present on the server. Not authentication:
   * only a completed provider request establishes that the key works.
   */
  model_configured_locally: boolean;
  configuration_problems: string[];
  configuration_note: string;
  implemented: string[];
  not_implemented: string[];
}

export type ConnectionState =
  | { kind: "checking" }
  | { kind: "connected"; health: HealthResponse }
  | { kind: "failed"; message: string };

export interface Objective {
  id: string;
  statement: string;
  rationale: string | null;
}

export interface Constraint {
  id: string;
  kind: string;
  value: string | null;
  notes: string | null;
}

export interface Initiative {
  id: string;
  name: string;
  description: string | null;
  claimed_objectives: string[];
}

export interface Brief {
  context_id: string;
  organisation: string;
  situation: string | null;
  objectives: Objective[];
  constraints: Constraint[];
  initiatives: Initiative[];
}

export interface SourceRef {
  kind: string;
  ref_id: string;
}

export interface Claim {
  statement: string;
  sources: SourceRef[];
}

export interface Gap {
  description: string;
  why_it_matters: string;
  relates_to: SourceRef[];
}

export interface Diagnosis {
  context_id: string;
  gaps: Gap[];
  contradictions: Gap[];
  unstated_assumptions: Gap[];
  summary: string;
}

export interface ContextRequest {
  missing: { field: string; why_required: string }[];
  message: string;
}

export type AnswerStatus = "answered" | "skipped" | "unanswered";

/** A result's currency. Superseded entries appear only in the history. */
export type ResultStatus = "current" | "outdated" | "superseded";

export interface Question {
  id: string;
  question: string;
  why_it_matters: string;
  /** What the manager did with it. */
  status: AnswerStatus;
  round: number;
  /**
   * Whether this question is still waiting for a reply. Different from status:
   * an unanswered question in a round already submitted is an open unknown,
   * not a request for input.
   */
  awaiting_response: boolean;
  /**
   * What the manager actually wrote. Null unless they answered.
   *
   * A non-null value means a reply was submitted. It does not mean the reply
   * addressed the question, nor that the gap the question was about is closed.
   */
  answer: string | null;
}

export interface HistoryEntry {
  action: string;
  turn: number;
  answers_version: number;
  created_at: string;
  status: ResultStatus;
}

export interface MissingEvidence {
  description: string;
  why_it_matters: string;
  how_it_could_be_resolved: string | null;
}

export interface InitiativeComparison {
  initiative_id: string;
  stated_facts: Claim[];
  assumptions: Claim[];
  missing_evidence: MissingEvidence[];
  feasibility_constraints: Claim[];
  trade_offs: Claim[];
}

export interface Comparison {
  context_id: string;
  criteria_considered: string[];
  initiatives: InitiativeComparison[];
  cross_cutting_notes: Claim[];
}

export type Stance =
  | "recommended"
  | "consider_later"
  | "not_recommended"
  | "insufficient_information";

export interface RecommendedItem {
  initiative_id: string;
  stance: Stance;
  rationale: string;
  supported_by: SourceRef[];
  rests_on_assumptions: string[];
}

export interface Recommendation {
  context_id: string;
  summary: string;
  items: RecommendedItem[];
  risks: { description: string; consequence_if_realised: string; early_signal: string | null }[];
  first_actions: { action: string; purpose: string; resolves_unknown: string | null }[];
  open_unknowns: string[];
  confidence_note: string;
}

export interface AdvisoryError {
  kind: string;
  message: string;
  recoverable?: boolean;
  details?: string[];
}

export interface SessionView {
  session_id: string;
  status: string;
  context_id: string;
  brief: Brief;
  diagnosis: Diagnosis | null;
  context_request: ContextRequest | null;
  questions: Question[];
  open_questions: { id: string; question: string; status: string }[];
  comparison: Comparison | null;
  comparison_status: ResultStatus | null;
  /** Only ever a current recommendation. */
  recommendation: Recommendation | null;
  /** A recommendation the manager's later answers have overtaken. */
  previous_recommendation: Recommendation | null;
  recommendation_status: ResultStatus | null;
  answers_version: number;
  history: HistoryEntry[];
  /** True while a clarification round is waiting to be submitted. */
  awaiting_answers: boolean;
  error: AdvisoryError | null;
  stopped_because: string | null;
  actions_taken?: string[];
}

/** An error carrying what the backend said, so the interface can be specific. */
export class ApiError extends Error {
  readonly advisory: AdvisoryError;

  constructor(advisory: AdvisoryError) {
    super(advisory.message);
    this.advisory = advisory;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(path, {
      ...init,
      headers: { Accept: "application/json", "Content-Type": "application/json", ...init?.headers },
    });
  } catch (cause) {
    throw new ApiError({
      kind: "network",
      message: "Could not reach the backend. Is it running?",
      recoverable: true,
    });
  }

  if (!response.ok) {
    let advisory: AdvisoryError = {
      kind: "http",
      message: `The backend returned ${response.status}.`,
      recoverable: response.status >= 500,
    };
    try {
      const body = await response.json();
      const detail = body?.detail;
      if (detail && typeof detail === "object" && "message" in detail) {
        advisory = { kind: detail.kind ?? "http", ...detail };
      } else if (response.status === 422) {
        advisory = {
          kind: "invalid_brief",
          message: "The brief is not valid. Check that every field is filled in correctly.",
          recoverable: true,
        };
      }
    } catch {
      // Body was not JSON; the generic message above stands.
    }
    throw new ApiError(advisory);
  }

  return (await response.json()) as T;
}

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch("/api/health", { signal: signal ?? null });
  if (!response.ok) {
    throw new Error(`Backend returned ${response.status} ${response.statusText}`);
  }
  return (await response.json()) as HealthResponse;
}

export async function fetchScenario(): Promise<{ scenario_id: string; label: string; brief: Brief }> {
  return request("/api/scenario");
}

export async function startSession(brief: Brief): Promise<SessionView> {
  return request("/api/sessions", { method: "POST", body: JSON.stringify({ brief }) });
}

export async function submitAnswers(
  sessionId: string,
  answers: Record<string, string>,
  skipped: string[],
): Promise<SessionView> {
  return request(`/api/sessions/${sessionId}/answers`, {
    method: "POST",
    body: JSON.stringify({ answers, skipped }),
  });
}

export async function continueSession(sessionId: string): Promise<SessionView> {
  return request(`/api/sessions/${sessionId}/continue`, { method: "POST" });
}
