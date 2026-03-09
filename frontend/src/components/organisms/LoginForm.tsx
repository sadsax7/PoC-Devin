/**
 * @fileoverview LoginForm organism component.
 *
 * Step 1 of the authentication flow: collects phone and password,
 * submits to the backend, and transitions to MFA if required.
 *
 * @remarks
 * HU-FE-03: Acceptance Criteria #1, #2, #4 (Login form, states, navigation).
 * FRONTEND-GUIDELINES.md §3.3 — Organisms: invoke domain hooks, manage local state.
 *
 * @example
 * ```tsx
 * import { LoginForm } from '@/components/organisms';
 *
 * <LoginForm
 *   onMfaRequired={(token) => setTempToken(token)}
 *   navigateFn={(path) => router.push(path)}
 * />
 * ```
 */

import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Button, ErrorMessage, TextField } from '@/components/atoms';
import { useLogin } from '@/lib/auth/useLogin';

// ---------------------------------------------------------------------------
// Validation helpers (reused from registration conventions)
// ---------------------------------------------------------------------------

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

// ---------------------------------------------------------------------------
// Visibility toggle sub-component
// ---------------------------------------------------------------------------

/** Props for the password visibility toggle. */
interface PasswordToggleProps {
  visible: boolean;
  onToggle: () => void;
}

/**
 * Small inline button to toggle password visibility.
 *
 * @param props - {@link PasswordToggleProps}
 * @returns A toggle button element.
 * @internal
 */
function PasswordToggle({ visible, onToggle }: PasswordToggleProps): React.ReactElement {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="text-gray-400 hover:text-gray-200"
      aria-label={visible ? 'Ocultar contraseña' : 'Mostrar contraseña'}
    >
      {visible ? '🙈' : '👁'}
    </button>
  );
}

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/**
 * Props for the {@link LoginForm} component.
 */
export interface LoginFormProps {
  /**
   * Called when the backend requires an MFA step.
   * Receives the temporary token to pass to the MFA form.
   */
  onMfaRequired?: (tempToken: string) => void;

  /** Additional CSS classes for the root section. */
  className?: string;

  /** Path to the logo image. @defaultValue `'/next.svg'` */
  logoSrc?: string;

  /** Alt text for the logo. @defaultValue `'Billetera Virtual logo'` */
  logoAlt?: string;

  /** Override navigation function (useful for testing). */
  navigateFn?: (path: string) => void;
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * LoginForm organism — Step 1 of the authentication flow.
 *
 * Renders phone and password fields with real-time E.164 validation.
 * Delegates submission to {@link useLogin} and transitions to the MFA
 * step by calling `onMfaRequired` when the backend requires it.
 *
 * @param props - {@link LoginFormProps}
 * @returns A styled login form section.
 */
export function LoginForm({
  onMfaRequired,
  className = '',
  logoSrc = '/next.svg',
  logoAlt = 'Billetera Virtual logo',
  navigateFn,
}: LoginFormProps): React.ReactElement {
  const { login, isLoading, error: apiError, needsMfa, tempToken } = useLogin(navigateFn);

  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [phoneError, setPhoneError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  // Notify parent when MFA is required
  useEffect(() => {
    if (needsMfa && tempToken) {
      onMfaRequired?.(tempToken);
    }
  }, [needsMfa, tempToken, onMfaRequired]);

  // Form is valid only when both fields pass their validations
  const isFormValid = useMemo(
    () => validateLoginPhone(phone) === '' && validateLoginPassword(password) === '',
    [phone, password],
  );

  const handlePhoneChange = useCallback((e: React.ChangeEvent<HTMLInputElement>): void => {
    const val = e.target.value;
    setPhone(val);
    if (val) setPhoneError(validateLoginPhone(val));
    else setPhoneError('');
  }, []);

  const handlePasswordChange = useCallback((e: React.ChangeEvent<HTMLInputElement>): void => {
    setPassword(e.target.value);
  }, []);

  const handleSubmit = useCallback(
    async (e: React.FormEvent): Promise<void> => {
      e.preventDefault();
      const pErr = validateLoginPhone(phone);
      if (pErr) {
        setPhoneError(pErr);
        return;
      }
      await login(phone, password);
    },
    [login, phone, password],
  );

  return (
    <section
      className={`flex min-h-screen flex-col items-center justify-center p-6 bg-background text-foreground ${className}`.trim()}
      aria-label="Formulario de inicio de sesión"
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={logoSrc} alt={logoAlt} width={120} height={48} className="dark:invert mb-8" />

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm flex flex-col gap-5"
        aria-label="Iniciar sesión"
        noValidate
      >
        <h1 className="text-2xl font-bold text-center">Iniciar sesión</h1>

        {/* c8 ignore next */}
        {apiError && <ErrorMessage message={apiError} />}

        <TextField
          id="phone"
          label="Teléfono"
          type="text"
          placeholder="ej: +573001234567"
          value={phone}
          onChange={handlePhoneChange}
          error={phoneError}
          disabled={isLoading}
        />

        <TextField
          id="password"
          label="Contraseña"
          type={showPassword ? 'text' : 'password'}
          placeholder="Tu contraseña"
          value={password}
          onChange={handlePasswordChange}
          disabled={isLoading}
          suffix={
            <PasswordToggle visible={showPassword} onToggle={() => setShowPassword((v) => !v)} />
          }
        />

        <Button
          variant="solid"
          fullWidth
          disabled={!isFormValid || isLoading}
          ariaBusy={isLoading}
          className="mt-2"
        >
          {isLoading ? 'Iniciando sesión...' : 'Ingresar'}
        </Button>

        <Button variant="outline" fullWidth href="/auth/register" disabled={isLoading}>
          ¿No tienes cuenta? Regístrate
        </Button>
      </form>
    </section>
  );
}
