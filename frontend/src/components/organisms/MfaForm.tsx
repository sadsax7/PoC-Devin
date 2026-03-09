/**
 * @fileoverview MfaForm organism component.
 *
 * Step 2 of the authentication flow: accepts a 6-digit OTP code,
 * verifies it against the backend, and completes authentication.
 *
 * @remarks
 * HU-FE-03: Acceptance Criteria #3, #4 (MFA form, states, error handling).
 * FRONTEND-GUIDELINES.md §3.3 — Organisms: invoke domain hooks, manage local state.
 *
 * @example
 * ```tsx
 * import { MfaForm } from '@/components/organisms';
 *
 * <MfaForm
 *   tempToken={token}
 *   onBackToLogin={() => setStep('login')}
 *   navigateFn={(path) => router.push(path)}
 * />
 * ```
 */

import React, { useCallback, useState } from 'react';
import { Button, ErrorMessage } from '@/components/atoms';
import { OtpCodeInput } from '@/components/molecules';
import { useMfa } from '@/lib/auth/useMfa';

// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------

/**
 * Props for the {@link MfaForm} component.
 */
export interface MfaFormProps {
  /**
   * Single-use temporary token returned by the login endpoint
   * when MFA is required. Must be forwarded to the verification endpoint.
   */
  tempToken: string;

  /**
   * Called to reset the flow back to the login step.
   * Invoked on 429 errors (after delay) and on token expiry (immediately).
   */
  onBackToLogin?: () => void;

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
 * MfaForm organism — Step 2 of the authentication flow.
 *
 * Renders a 6-digit OTP input, auto-submits on completion, and
 * handles error states with accessible feedback. Uses {@link useMfa}
 * to manage the verification lifecycle.
 *
 * @param props - {@link MfaFormProps}
 * @returns A styled MFA verification form section.
 */
export function MfaForm({
  tempToken,
  onBackToLogin,
  className = '',
  logoSrc = '/next.svg',
  logoAlt = 'Billetera Virtual logo',
  navigateFn,
}: MfaFormProps): React.ReactElement {
  const { verifyMfa, isLoading, error, attemptsRemaining } = useMfa(onBackToLogin, navigateFn);
  const [code, setCode] = useState('');

  const handleVerify = useCallback(
    async (submittedCode?: string): Promise<void> => {
      const codeToSubmit = submittedCode ?? code;
      if (codeToSubmit.length < 6) return;
      await verifyMfa(tempToken, codeToSubmit);
      setCode('');
    },
    [verifyMfa, tempToken, code],
  );

  const handleOtpComplete = useCallback(
    async (completedCode: string): Promise<void> => {
      await handleVerify(completedCode);
    },
    [handleVerify],
  );

  const handleSubmit = useCallback(
    async (e: React.FormEvent): Promise<void> => {
      e.preventDefault();
      await handleVerify();
    },
    [handleVerify],
  );

  const isSubmitDisabled = isLoading || code.length < 6;

  return (
    <section
      className={`flex min-h-screen flex-col items-center justify-center p-6 bg-background text-foreground ${className}`.trim()}
      aria-label="Verificación MFA"
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={logoSrc} alt={logoAlt} width={120} height={48} className="dark:invert mb-8" />

      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm flex flex-col gap-6"
        aria-label="Verificación de seguridad"
        noValidate
      >
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">Verificación de Seguridad</h1>
          <p className="text-sm text-gray-400">
            Ingresa el código de 6 dígitos generado por tu aplicación de autenticación
          </p>
        </div>

        {/* c8 ignore next */}
        {error && <ErrorMessage message={error} />}

        {/* c8 ignore next */}
        {!error && attemptsRemaining < 3 && attemptsRemaining > 0 && (
          <p className="text-sm text-yellow-400 text-center" aria-live="polite">
            Intentos restantes: {attemptsRemaining}
          </p>
        )}

        <OtpCodeInput
          value={code}
          onChange={setCode}
          onComplete={handleOtpComplete}
          disabled={isLoading}
          hasError={Boolean(error)}
        />

        <Button variant="solid" fullWidth disabled={isSubmitDisabled} ariaBusy={isLoading}>
          {isLoading ? 'Verificando...' : 'Verificar'}
        </Button>

        <Button variant="outline" fullWidth onClick={() => onBackToLogin?.()} disabled={isLoading}>
          Volver a login
        </Button>
      </form>
    </section>
  );
}
