import type { MetricSample } from './metricsBuffer';

export const DEFAULT_API_BASE = 'http://127.0.0.1:8000';

export type ApiFailure = { ok: false; retry: boolean; unauthorized: boolean; message: string };

function trimBase(baseUrl: string): string {
  return baseUrl.trim().replace(/\/+$/, '');
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === 'string') return body.detail;
  } catch {
    /* The body was not JSON. */
  }
  return `Sunucu ${response.status} döndü.`;
}

/**
 * Posts JSON numbers. A network failure, 5xx, or 429 is retried later.
 * A 401 clears the sign-in. A 422 keeps the rows and does not sign the user out.
 */
export async function postJson<T>(
  baseUrl: string,
  path: string,
  body: unknown,
  token: string | null,
): Promise<{ ok: true; status: number; body: T } | ApiFailure> {
  try {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = `Bearer ${token}`;
    const response = await fetch(`${trimBase(baseUrl)}${path}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
    });
    if (response.ok) {
      if (response.status === 204) return { ok: true, status: response.status, body: undefined as T };
      return { ok: true, status: response.status, body: (await response.json()) as T };
    }
    const retry = response.status >= 500 || response.status === 429;
    return { ok: false, retry, unauthorized: response.status === 401, message: await errorMessage(response) };
  } catch {
    return {
      ok: false,
      retry: true,
      unauthorized: false,
      message: 'Sunucuya ulaşılamadı. Satırlar kuyrukta bekliyor.',
    };
  }
}

export async function login(
  baseUrl: string,
  email: string,
  password: string,
): Promise<{ ok: true; token: string } | ApiFailure> {
  const result = await postJson<{ access_token: string }>(baseUrl, '/api/v1/auth/login', { email, password }, null);
  if (!result.ok) return result;
  return { ok: true, token: result.body.access_token };
}

export async function startSession(baseUrl: string, token: string): Promise<{ ok: true; id: string } | ApiFailure> {
  const result = await postJson<{ id: string }>(baseUrl, '/api/v1/sessions', { device: 'webcam' }, token);
  if (!result.ok) return result;
  return { ok: true, id: result.body.id };
}

export async function sendMetrics(
  baseUrl: string,
  token: string,
  sessionId: string,
  samples: readonly MetricSample[],
): Promise<{ ok: true; accepted: number } | ApiFailure> {
  const result = await postJson<{ accepted: number }>(
    baseUrl,
    '/api/v1/metrics',
    { session_id: sessionId, samples },
    token,
  );
  if (!result.ok) return result;
  return { ok: true, accepted: result.body.accepted };
}
