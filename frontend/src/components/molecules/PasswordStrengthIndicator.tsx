/**
 * @fileoverview PasswordStrengthIndicator molecule component.
 *
 * Renders a visual progress bar indicating password strength.
 * Uses red (weak), yellow (medium), and green (strong) colour coding.
 *
 * @remarks
 * HU-FE-02: Acceptance Criteria #2 (password strength indicator).
 * FRONTEND-GUIDELINES.md §3.2 — Molecules.
 *
 * @example
 * ```tsx
 * import { PasswordStrengthIndicator } from '@/components/molecules';
 *
 * <PasswordStrengthIndicator password={passwordValue} />
 * ```
 */

import React from 'react';

/** Visual strength level for the password indicator. */
export type PasswordStrength = 'none' | 'weak' | 'medium' | 'strong';

/**
 * Props for the {@link PasswordStrengthIndicator} component.
 */
export interface PasswordStrengthIndicatorProps {
  /** The current password value to evaluate. */
  password: string;

  /** Additional CSS classes for the root wrapper. */
  className?: string;
}

/**
 * Colour mapping for each strength level.
 * @internal
 */
const STRENGTH_COLORS: Record<PasswordStrength, string> = {
  none: 'bg-white/20',
  weak: 'bg-red-500',
  medium: 'bg-yellow-500',
  strong: 'bg-green-500',
};

/**
 * Label mapping for each strength level (used in aria-label).
 * @internal
 */
const STRENGTH_LABELS: Record<PasswordStrength, string> = {
  none: 'Sin contraseña',
  weak: 'Contraseña débil',
  medium: 'Contraseña media',
  strong: 'Contraseña fuerte',
};

/**
 * Width percentage mapping for each strength level.
 * @internal
 */
const STRENGTH_WIDTH: Record<PasswordStrength, string> = {
  none: 'w-0',
  weak: 'w-1/3',
  medium: 'w-2/3',
  strong: 'w-full',
};

/**
 * Calculate the strength level of a given password.
 *
 * Rules evaluated:
 * - Length >= 8 characters
 * - Contains uppercase letter
 * - Contains lowercase letter
 * - Contains digit
 * - Contains special character
 *
 * @param password - The password string to evaluate.
 * @returns The computed {@link PasswordStrength} level.
 */
export function calculateStrength(password: string): PasswordStrength {
  if (!password) {
    return 'none';
  }

  let score = 0;
  if (password.length >= 8) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[a-z]/.test(password)) score++;
  if (/\d/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;

  if (score <= 2) return 'weak';
  if (score <= 4) return 'medium';
  return 'strong';
}

/**
 * PasswordStrengthIndicator molecule — a visual bar for password strength.
 *
 * Evaluates the provided password against common rules and renders
 * a coloured progress bar with an accessible label.
 *
 * @param props - {@link PasswordStrengthIndicatorProps}
 * @returns A strength indicator element.
 */
export function PasswordStrengthIndicator({
  password,
  className = '',
}: PasswordStrengthIndicatorProps): React.ReactElement {
  const strength = calculateStrength(password);

  return (
    <div className={`flex flex-col gap-1 ${className}`.trim()}>
      <div
        className="h-2 w-full rounded-full bg-white/10"
        role="progressbar"
        aria-label={STRENGTH_LABELS[strength]}
        aria-valuenow={
          strength === 'none' ? 0 : strength === 'weak' ? 33 : strength === 'medium' ? 66 : 100
        }
        aria-valuemin={0}
        aria-valuemax={100}
      >
        <div
          className={`h-full rounded-full transition-all ${STRENGTH_COLORS[strength]} ${STRENGTH_WIDTH[strength]}`}
        />
      </div>
      {strength !== 'none' && (
        <span
          className={`text-xs ${strength === 'weak' ? 'text-red-500' : strength === 'medium' ? 'text-yellow-500' : 'text-green-500'}`}
        >
          {STRENGTH_LABELS[strength]}
        </span>
      )}
    </div>
  );
}
