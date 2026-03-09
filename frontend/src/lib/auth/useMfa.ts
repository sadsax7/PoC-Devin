/**
 * @fileoverview useMfa — UI use-case hook for MFA verification.
 *
 * Encapsulates the MFA code verification workflow: submission, loading state,
 * error mapping with attempt counters, and post-success redirect to `/dashboard`.
 *
 * @remarks
 * HU-FE-03: Acceptance Criteria #3, #8 (MFA verification, UI hook).
 * FRONTEND-GUIDELINES.md §4.2 — UI Use Case Hook pattern.
 *
 * @example
 * ```tsx
 * const { verifyMfa, isLoading, error, attemptsRemaining } = useMfa(onBack);
 *
 * await verifyMfa(tempToken, '123456');
 * ```
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { apiClient, type ApiError } from '@/lib/api/client';

/**
 * Shape of the MFA verification endpoint response.
 */
interface MfaApiResponse {
  /** Full access token issued after MFA succeeds. */
  access_token: string;
  /** Refresh token for silent re-authentication. */
  refresh_token: string;
  /** Token type, should be "Bearer". */
  token_type: string;
  /** Token lifetime in seconds. */
  expires_in: number;
}

/**
 * Milliseconds to wait before redirecting back to login after too many MFA attempts.
 */
const MFA_REDIRECT_DELAY_MS = 3000;

/**
 * Extract remaining attempt count from an MFA API error response.
 *
 * The backend embeds the count in the detail string as "N attempts remaining".
 *
 * @param err - The structured API error from the client.
 * @returns The number of attempts remaining, or null if not present.
 */
export function extractAttemptsRemaining(err: ApiError): number | null {
  const detailStr = String((err.detail as Record<string, unknown>)?.detail ?? err.detail ?? '');
  const match = /(\d+) attempts remaining/i.exec(detailStr);
  if (match) return parseInt(match[1], 10);
  return null;
}

/**
 * Classify and map an MFA API error to a user-facing message and state.
 *
 * @param err - The structured API error from the client.
 * @returns A tuple of `[message, attemptsRemaining, isExpired]`.
 */
export function mapMfaError(err: ApiError): {
  message: string;
  remaining: number;
  isExpired: boolean;
  isTooMany: boolean;
} {
  if (err.status === 429) {
    return {
      message: 'Demasiados intentos fallidos. Redirigiendo a login...',
      remaining: 0,
      isExpired: false,
      isTooMany: true,
    };
  }

  if (err.status === 401) {
    const remaining = extractAttemptsRemaining(err);
    if (remaining !== null) {
      return {
        message: `Código incorrecto. Intentos restantes: ${remaining}`,
        remaining,
        isExpired: false,
        isTooMany: false,
      };
    }
    return {
      message: 'Sesión expirada. Vuelve a iniciar sesión.',
      remaining: 0,
      isExpired: true,
      isTooMany: false,
    };
  }

  return {
    message: 'Error del servidor. Intenta nuevamente más tarde.',
    remaining: 0,
    isExpired: false,
    isTooMany: false,
  };
}

/**
 * Return type for the {@link useMfa} hook.
 */
export interface UseMfaReturn {
  /**
   * Submit an OTP code along with the temporary token.
   * @param tempToken - Single-use token from the login step.
   * @param code - 6-digit OTP code entered by the user.
   */
  verifyMfa: (tempToken: string, code: string) => Promise<void>;

  /** Whether a verification request is currently in-flight. */
  isLoading: boolean;

  /** User-facing error message from the last failed attempt. */
  error: string;

  /** Number of MFA attempts remaining after the last failure. */
  attemptsRemaining: number;
}

/**
 * UI use-case hook for MFA code verification.
 *
 * Manages loading / error / retry-count state and delegates HTTP calls
 * to the API client. On success, redirects to `/dashboard`.
 * On 429 (too many attempts), shows a countdown message and calls
 * `onBackToLogin` after {@link MFA_REDIRECT_DELAY_MS} milliseconds.
 * On session expiry (401 without attempt count), calls `onBackToLogin` immediately.
 *
 * @param onBackToLogin - Callback invoked to reset the flow to the login step.
 * @param navigateFn - Optional navigation override. Defaults to `window.location.assign`.
 * @returns An object with `verifyMfa`, `isLoading`, `error`, and `attemptsRemaining`.
 */
export function useMfa(
  onBackToLogin?: () => void,
  navigateFn?: (path: string) => void,
): UseMfaReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [attemptsRemaining, setAttemptsRemaining] = useState(3);

  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const navigateRef = useRef(navigateFn ?? ((path: string) => window.location.assign(path)));
  const onBackRef = useRef(onBackToLogin);

  useEffect(() => {
    navigateRef.current = navigateFn ?? ((path: string) => window.location.assign(path));
  }, [navigateFn]);

  useEffect(() => {
    onBackRef.current = onBackToLogin;
  }, [onBackToLogin]);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, []);

  const verifyMfa = useCallback(async (tempToken: string, code: string): Promise<void> => {
    setIsLoading(true);
    setError('');

    try {
      await apiClient<MfaApiResponse>('/auth/mfa/verify', {
        method: 'POST',
        body: JSON.stringify({ temp_token: tempToken, code }),
      });
      navigateRef.current('/dashboard');
    } catch (err) {
      const { message, remaining, isExpired, isTooMany } = mapMfaError(err as ApiError);
      setError(message);
      setAttemptsRemaining(remaining);

      if (isTooMany) {
        timerRef.current = setTimeout(() => {
          onBackRef.current?.();
        }, MFA_REDIRECT_DELAY_MS);
      } else if (isExpired) {
        onBackRef.current?.();
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { verifyMfa, isLoading, error, attemptsRemaining };
}
