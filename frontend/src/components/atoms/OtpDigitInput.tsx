/**
 * @fileoverview OtpDigitInput atom component.
 *
 * A single-digit numeric input for OTP/MFA code entry.
 * Uses the same visual design language as {@link TextField}.
 *
 * @remarks
 * HU-FE-03: Acceptance Criteria #3 (OTP input), #5 (atoms), #7 (accessibility).
 * FRONTEND-GUIDELINES.md §3.1 — Atoms: no business logic, only props + events.
 *
 * @example
 * ```tsx
 * import { OtpDigitInput } from '@/components/atoms';
 *
 * <OtpDigitInput
 *   id="otp-0"
 *   index={0}
 *   value={digits[0]}
 *   onChange={handleChange}
 *   onKeyDown={handleKeyDown}
 *   inputRef={refs[0]}
 * />
 * ```
 */

import React from 'react';

/**
 * Props for the {@link OtpDigitInput} component.
 */
export interface OtpDigitInputProps {
  /** Unique HTML id for the input element. */
  id: string;

  /**
   * Zero-based position index (0–5).
   * Used to compute the `aria-label` ("Dígito N de 6").
   */
  index: number;

  /** The current single-digit value: "" or "0"–"9". */
  value: string;

  /**
   * Called with the accepted digit and its index on every change.
   * Non-numeric characters are stripped before this is called.
   */
  onChange: (value: string, index: number) => void;

  /**
   * Keyboard event handler forwarded from the parent molecule.
   * Allows the parent to handle Backspace navigation.
   */
  onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>, index: number) => void;

  /** Whether the input is disabled (e.g. while submitting). */
  disabled?: boolean;

  /** Whether to render error styling (red border). */
  hasError?: boolean;

  /** Ref for programmatic focus management by the parent molecule. */
  inputRef?: React.RefCallback<HTMLInputElement>;

  /** Additional CSS classes appended to the input element. */
  className?: string;
}

/**
 * OtpDigitInput atom — a single numeric digit input for OTP codes.
 *
 * Renders a styled square input accepting exactly one digit (0–9).
 * Non-numeric input is silently ignored. Accessible via `aria-label`.
 *
 * @param props - {@link OtpDigitInputProps}
 * @returns A styled single-digit input element.
 */
export function OtpDigitInput({
  id,
  index,
  value,
  onChange,
  onKeyDown,
  disabled = false,
  hasError = false,
  inputRef,
  className = '',
}: OtpDigitInputProps): React.ReactElement {
  const borderClass = hasError
    ? 'border-red-500 focus:ring-red-500'
    : 'border-gray-500 focus:ring-primary';

  function handleChange(e: React.ChangeEvent<HTMLInputElement>): void {
    const raw = e.target.value.replace(/\D/g, '');
    const digit = raw.slice(-1);
    onChange(digit, index);
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>): void {
    onKeyDown(e, index);
  }

  return (
    <input
      ref={inputRef}
      id={id}
      type="text"
      inputMode="numeric"
      pattern="[0-9]*"
      maxLength={1}
      value={value}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      aria-label={`Dígito ${index + 1} de 6`}
      autoComplete="one-time-code"
      className={`w-12 h-12 text-center text-xl font-semibold rounded-lg border-2
        bg-background text-foreground
        focus:outline-none focus:ring-2 focus:ring-offset-1
        disabled:opacity-50 disabled:cursor-not-allowed
        ${borderClass} ${className}`.trim()}
    />
  );
}
