/**
 * @fileoverview useLogin — UI use-case hook for user login.
 *
 * Encapsulates the login workflow: credential submission, loading state,
 * error mapping, MFA-required routing, and post-success redirect to `/dashboard`.
 *
 * @remarks
 * HU-FE-03: Acceptance Criteria #2, #8 (backend integration, UI hook).
 * FRONTEND-GUIDELINES.md §4.2 — UI Use Case Hook pattern.
 *
 * @example
 * ```tsx
 * const { login, isLoading, error, needsMfa, tempToken } = useLogin();
 *
 * await login('+573001234567', 'Secure@123');
 * // If needsMfa === true, flow transitions to MFA step with tempToken.
 * ```
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { apiClient, type ApiError } from '@/lib/api/client';

/**
 * Shape of the login endpoint response.
 * Both direct login and MFA-required scenarios use the same endpoint.
 */
interface LoginApiResponse {
  /** Present on direct login (MFA disabled). */
  access_token?: string;
  /** Present on direct login (MFA disabled). */
  refresh_token?: string;
  /** Present when MFA is required instead of a full access token. */
  temp_token?: string;
  /** True when the backend requires an MFA step. */
  mfa_required?: boolean;
  /** Token type string, should be "Bearer". */
  token_type?: string;
  /** Token lifetime in seconds. */
  expires_in?: number;
}

/** E.164 phone regex: + followed by 7–15 digits. */
const E164_REGEX = /^\+\d{7,15}$/;

/**
 * Validate a phone number in E.164 format.
 *
 * @param value - Phone string to validate.
 * @returns Error message or empty string.
 */
export function validateLoginPhone(value: string): string {
  if (!value) return 'El teléfono es obligatorio.';
  if (!E164_REGEX.test(value)) return 'Formato inválido. Usa +[código país][número]';
  return '';
}

/**
 * Validate that the password field is not empty.
 *
 * @param value - Password string.
 * @returns Error message or empty string.
 */
export function validateLoginPassword(value: string): string {
  if (!value) return 'La contraseña es obligatoria.';
  return '';
}

/**
 * Map a login API error to a user-facing message.
 *
 * @param err - The structured API error from the client.
 * @returns A localised string for display.
 */
export function mapLoginError(err: ApiError): string {
  switch (err.status) {
    case 401:
      return 'Credenciales inválidas. Verifica tu teléfono y contraseña.';
    case 404:
      return 'Teléfono no registrado. ¿Quieres registrarte?';
    case 423:
      return 'Tu cuenta está bloqueada. Contacta soporte.';
    default:
      return 'Error del servidor. Intenta nuevamente más tarde.';
  }
}

/**
 * Return type for the {@link useLogin} hook.
 */
export interface UseLoginReturn {
  /**
   * Submit login credentials to the backend.
   * @param phone - Phone number in E.164 format.
   * @param password - User password.
   */
  login: (phone: string, password: string) => Promise<void>;

  /** Whether a login request is currently in-flight. */
  isLoading: boolean;

  /** User-facing error message from the last failed attempt. */
  error: string;

  /** True when the backend requires an MFA verification step. */
  needsMfa: boolean;

  /**
   * Temporary token to pass to the MFA verification endpoint.
   * Only set when {@link needsMfa} is true.
   */
  tempToken: string;
}

/**
 * UI use-case hook for user login.
 *
 * Manages loading / error / MFA-required state and delegates HTTP calls
 * to the API client. On direct success, redirects to `/dashboard`.
 * On MFA required, exposes `needsMfa=true` and `tempToken`.
 *
 * @param navigateFn - Optional navigation override. Defaults to `window.location.assign`.
 * @returns An object with `login`, `isLoading`, `error`, `needsMfa`, and `tempToken`.
 */
export function useLogin(navigateFn?: (path: string) => void): UseLoginReturn {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [needsMfa, setNeedsMfa] = useState(false);
  const [tempToken, setTempToken] = useState('');

  const navigateRef = useRef(navigateFn ?? ((path: string) => window.location.assign(path)));

  useEffect(() => {
    navigateRef.current = navigateFn ?? ((path: string) => window.location.assign(path));
  }, [navigateFn]);

  const login = useCallback(async (phone: string, password: string): Promise<void> => {
    setIsLoading(true);
    setError('');
    setNeedsMfa(false);
    setTempToken('');

    try {
      const data = await apiClient<LoginApiResponse>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ phone, password }),
      });

      if (data.mfa_required && data.temp_token) {
        setTempToken(data.temp_token);
        setNeedsMfa(true);
      } else if (data.access_token) {
        navigateRef.current('/dashboard');
      }
    } catch (err) {
      setError(mapLoginError(err as ApiError));
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { login, isLoading, error, needsMfa, tempToken };
}
