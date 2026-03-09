/**
 * @fileoverview useRegister — UI use-case hook for user registration.
 *
 * Encapsulates the registration workflow: form data submission, loading state,
 * error mapping, and post-success redirect to `/auth/login`.
 *
 * @remarks
 * HU-FE-02: Acceptance Criteria #4, #8 (backend integration, UI hook).
 * FRONTEND-GUIDELINES.md §4.2 — UI Use Case Hook pattern.
 *
 * @example
 * ```tsx
 * const { register, isLoading, error, success } = useRegister();
 *
 * await register({ phone: '+573001234567', password: 'Secure@123' });
 * ```
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { apiClient, type ApiError } from '@/lib/api/client';

/**
 * Payload accepted by the registration endpoint.
 */
export interface RegisterFormData {
  /** Phone number in E.164 format. */
  phone: string;

  /** User password (8-128 chars, mixed case, digit, special). */
  password: string;

  /** Optional email address. */
  email?: string;

  /** Optional user display name. */
  name?: string;
}

/** Internal state managed by the hook. */
interface RegisterState {
  /** Whether a request is in-flight. */
  isLoading: boolean;

  /** Error message from the last failed attempt. */
  error: string;

  /** Whether the last attempt succeeded. */
  success: boolean;
}

/**
 * Map an API status code to a user-friendly error message.
 *
 * @param err - The structured API error.
 * @returns A localised error string for the UI.
 */
function mapApiError(err: ApiError): string {
  switch (err.status) {
    case 400:
      return 'Tu número de teléfono no pasó la verificación KYC. Contacta soporte.';
    case 409:
      return 'Este teléfono ya está registrado. ¿Quieres iniciar sesión?';
    case 422: {
      if (Array.isArray((err.detail as Record<string, unknown>)?.detail)) {
        return ((err.detail as Record<string, unknown>).detail as Array<{ msg: string }>)
          .map((d) => d.msg)
          .join('. ');
      }
      return 'Datos inválidos. Revisa los campos e intenta de nuevo.';
    }
    default:
      return 'Error del servidor. Intenta nuevamente más tarde.';
  }
}

/** Redirect delay in milliseconds after successful registration. */
const REDIRECT_DELAY_MS = 2000;

/**
 * Return type for the {@link useRegister} hook.
 */
export interface UseRegisterReturn {
  /** Submit the registration form data. */
  register: (data: RegisterFormData) => Promise<void>;

  /** Whether a request is currently in-flight. */
  isLoading: boolean;

  /** Error message from the last failed attempt. */
  error: string;

  /** Whether the last registration succeeded. */
  success: boolean;
}

/**
 * UI use-case hook for user registration.
 *
 * Manages loading / error / success state and delegates HTTP calls
 * to the API client. On success, schedules a redirect to `/auth/login`
 * after {@link REDIRECT_DELAY_MS} milliseconds.
 *
 * @param navigateFn - Optional navigation callback. Defaults to `window.location.assign`.
 * @returns An object with `register`, `isLoading`, `error`, and `success`.
 */
export function useRegister(navigateFn?: (path: string) => void): UseRegisterReturn {
  const [state, setState] = useState<RegisterState>({
    isLoading: false,
    error: '',
    success: false,
  });

  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const navigateRef = useRef(navigateFn ?? ((path: string) => window.location.assign(path)));

  useEffect(() => {
    navigateRef.current = navigateFn ?? ((path: string) => window.location.assign(path));
  }, [navigateFn]);

  const register = useCallback(async (data: RegisterFormData): Promise<void> => {
    setState({ isLoading: true, error: '', success: false });

    try {
      await apiClient('/auth/register', {
        method: 'POST',
        body: JSON.stringify({
          phone: data.phone,
          password: data.password,
          ...(data.email ? { email: data.email } : {}),
          ...(data.name ? { name: data.name } : {}),
        }),
      });

      setState({ isLoading: false, error: '', success: true });

      timerRef.current = setTimeout(() => {
        navigateRef.current('/auth/login');
      }, REDIRECT_DELAY_MS);
    } catch (err: unknown) {
      const apiErr = err as ApiError;
      const message =
        typeof apiErr?.status === 'number'
          ? mapApiError(apiErr)
          : 'Error de conexión. Verifica tu red e intenta de nuevo.';

      setState({ isLoading: false, error: message, success: false });
    }
  }, []);

  return {
    register,
    isLoading: state.isLoading,
    error: state.error,
    success: state.success,
  };
}
