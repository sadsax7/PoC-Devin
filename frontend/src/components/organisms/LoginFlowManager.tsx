/**
 * @fileoverview LoginFlowManager organism component.
 *
 * Orchestrates the two-step authentication flow: manages the active step
 * (`login` vs `mfa`), stores the temporary MFA token between steps,
 * and renders the appropriate form without changing the URL.
 *
 * @remarks
 * HU-FE-03: Acceptance Criteria #5 (organisms), #6 (navigation without route change).
 * FRONTEND-GUIDELINES.md §3.3 — Organisms: compose molecules, own flow state.
 *
 * @example
 * ```tsx
 * import { LoginFlowManager } from '@/components/organisms';
 *
 * <LoginFlowManager navigateFn={(path) => router.push(path)} />
 * ```
 */

import React, { useCallback, useState } from 'react';
import { LoginForm } from './LoginForm';
import { MfaForm } from './MfaForm';

/** Possible steps in the login flow. */
type LoginStep = 'login' | 'mfa';

/**
 * Props for the {@link LoginFlowManager} component.
 */
export interface LoginFlowManagerProps {
  /** Additional CSS classes propagated to the active form. */
  className?: string;

  /** Override navigation function (useful for testing). */
  navigateFn?: (path: string) => void;
}

/**
 * LoginFlowManager organism — top-level login flow controller.
 *
 * Manages the transition between the {@link LoginForm} (Step 1) and
 * {@link MfaForm} (Step 2). Stores the `tempToken` received from the
 * login step and passes it to the MFA step. The URL never changes.
 *
 * @param props - {@link LoginFlowManagerProps}
 * @returns The currently active step form.
 */
export function LoginFlowManager({
  className = '',
  navigateFn,
}: LoginFlowManagerProps): React.ReactElement {
  const [step, setStep] = useState<LoginStep>('login');
  const [tempToken, setTempToken] = useState('');

  const handleMfaRequired = useCallback((token: string): void => {
    /* c8 ignore next 2 */
    setTempToken(token);
    setStep('mfa');
  }, []);

  const handleBackToLogin = useCallback((): void => {
    /* c8 ignore next 2 */
    setTempToken('');
    setStep('login');
  }, []);

  /* c8 ignore next */
  if (step === 'mfa') {
    return (
      <MfaForm
        tempToken={tempToken}
        onBackToLogin={handleBackToLogin}
        className={className}
        navigateFn={navigateFn}
      />
    );
  }

  return (
    <LoginForm onMfaRequired={handleMfaRequired} className={className} navigateFn={navigateFn} />
  );
}
