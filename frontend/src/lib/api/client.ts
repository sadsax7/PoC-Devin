/**
 * @fileoverview API client configuration.
 *
 * Provides a thin wrapper around `fetch` with the backend base URL,
 * JSON content-type header, and typed error handling.
 *
 * @remarks
 * FRONTEND-GUIDELINES.md §4.4 — Client HTTP.
 * HU-FE-02: Acceptance Criteria #4 (backend integration).
 *
 * @example
 * ```ts
 * import { apiClient } from '@/lib/api/client';
 *
 * const res = await apiClient('/auth/register', {
 *   method: 'POST',
 *   body: JSON.stringify(payload),
 * });
 * ```
 */

/** Base URL for the backend API. Uses env var or falls back to localhost. */
const API_BASE_URL: string =
  typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL
    ? process.env.NEXT_PUBLIC_API_URL
    : 'http://localhost:8000';

/**
 * Structured error returned by the API client on non-2xx responses.
 */
export interface ApiError {
  /** HTTP status code. */
  status: number;

  /** Human-readable error message. */
  message: string;

  /** Raw response body detail (if available). */
  detail?: unknown;
}

/**
 * Perform an API request to the backend.
 *
 * Automatically prepends the base URL and sets `Content-Type: application/json`.
 * On non-2xx responses, throws an {@link ApiError} with status and parsed body.
 *
 * @param path - The endpoint path (e.g. `/auth/register`).
 * @param init - Standard `RequestInit` options (method, body, headers, etc.).
 * @returns The parsed JSON response body.
 * @throws {ApiError} When the response status is not in the 200-299 range.
 */
export async function apiClient<T = unknown>(path: string, init?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  const response = await fetch(url, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...init?.headers,
    },
  });

  if (!response.ok) {
    let detail: unknown;
    try {
      detail = await response.json();
    } catch {
      detail = undefined;
    }

    const error: ApiError = {
      status: response.status,
      message: `Request failed with status ${response.status}`,
      detail,
    };
    throw error;
  }

  return response.json() as Promise<T>;
}
