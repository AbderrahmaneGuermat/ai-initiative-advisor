/**
 * Backend API client.
 *
 * Skeleton stage: the health endpoint only. Every request goes through /api,
 * which the Vite dev server proxies to the backend. No model provider is ever
 * called from the browser, and no API key reaches this code.
 */

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  stage: string;
  model_configured: boolean;
  offline_fixture_mode: boolean;
  implemented: string[];
  not_implemented: string[];
}

export type ConnectionState =
  | { kind: "checking" }
  | { kind: "connected"; health: HealthResponse }
  | { kind: "failed"; message: string };

export async function fetchHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch("/api/health", {
    signal: signal ?? null,
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Backend returned ${response.status} ${response.statusText}`);
  }

  return (await response.json()) as HealthResponse;
}
