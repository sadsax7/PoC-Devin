/**
 * @fileoverview OtpCodeInput molecule component.
 *
 * A group of six {@link OtpDigitInput} atoms that collectively capture
 * a 6-digit OTP code. Handles auto-advance, backspace navigation, and paste.
 *
 * @remarks
 * HU-FE-03: Acceptance Criteria #3 (OTP input behaviour), #5 (molecules).
 * FRONTEND-GUIDELINES.md §3.2 — Molecules: groups atoms, lightweight UI logic.
 *
 * @example
 * ```tsx
 * import { OtpCodeInput } from '@/components/molecules';
 *
 * <OtpCodeInput
 *   value={otpCode}
 *   onChange={setOtpCode}
 *   onComplete={handleAutoSubmit}
 *   hasError={Boolean(error)}
 * />
 * ```
 */

import React, { useCallback, useRef } from 'react';
import { OtpDigitInput } from '@/components/atoms';

/** Number of OTP digits. */
const OTP_LENGTH = 6;

/**
 * Props for the {@link OtpCodeInput} component.
 */
export interface OtpCodeInputProps {
  /**
   * The current code as a plain string (e.g. `"12"` or `"123456"`).
   * Characters beyond position 5 are ignored.
   * Missing characters are treated as empty digits.
   */
  value: string;

  /**
   * Called on every digit change with the full updated code string.
   * The string is always at most 6 characters of digits.
   */
  onChange: (code: string) => void;

  /**
   * Called when all 6 digits are filled (auto-submit trigger).
   * Receives the completed 6-digit code string.
   */
  onComplete?: (code: string) => void;

  /** Whether all inputs are disabled (e.g. while submitting). */
  disabled?: boolean;

  /** Whether to render error styling on all inputs. */
  hasError?: boolean;

  /** Additional CSS classes for the wrapper element. */
  className?: string;
}

/**
 * OtpCodeInput molecule — six individual digit inputs for OTP entry.
 *
 * Manages focus flow automatically:
 * - Typing a digit moves focus to the next input.
 * - Pressing Backspace on an empty input moves focus to the previous.
 * - Pasting a numeric string distributes digits and focuses appropriately.
 *
 * @param props - {@link OtpCodeInputProps}
 * @returns A group of six styled digit inputs.
 */
export function OtpCodeInput({
  value,
  onChange,
  onComplete,
  disabled = false,
  hasError = false,
  className = '',
}: OtpCodeInputProps): React.ReactElement {
  const inputRefs = useRef<Array<HTMLInputElement | null>>(Array(OTP_LENGTH).fill(null));

  /**
   * Callback ref factory for each digit input.
   * Stores the DOM element reference in {@link inputRefs} without
   * accessing `.current` during render (satisfies react-hooks/refs rule).
   */
  const makeInputRef = useCallback(
    (i: number) =>
      (el: HTMLInputElement | null): void => {
        inputRefs.current[i] = el;
      },
    [],
  );

  /** Normalise value into an array of OTP_LENGTH single-digit strings. */
  const digits = Array.from({ length: OTP_LENGTH }, (_, i) =>
    value[i] !== undefined ? value[i] : '',
  );

  const handleDigitChange = useCallback(
    (digit: string, index: number): void => {
      const newDigits = [...digits];
      newDigits[index] = digit;
      const newCode = newDigits.join('');
      onChange(newCode);

      if (digit && index < OTP_LENGTH - 1) {
        inputRefs.current[index + 1]?.focus();
      }

      if (digit && index === OTP_LENGTH - 1) {
        const completed = newDigits.join('');
        if (completed.length === OTP_LENGTH) {
          onComplete?.(completed);
        }
      }
    },
    [digits, onChange, onComplete],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>, index: number): void => {
      if (e.key === 'Backspace' && !digits[index] && index > 0) {
        inputRefs.current[index - 1]?.focus();
      }
    },
    [digits],
  );

  const handlePaste = useCallback(
    (e: React.ClipboardEvent): void => {
      e.preventDefault();
      const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, OTP_LENGTH);
      if (!pasted) return;

      const newDigits = Array.from({ length: OTP_LENGTH }, (_, i) =>
        pasted[i] !== undefined ? pasted[i] : '',
      );
      const newCode = newDigits.join('');
      onChange(newCode);

      const focusIndex = Math.min(pasted.length, OTP_LENGTH - 1);
      inputRefs.current[focusIndex]?.focus();

      if (pasted.length === OTP_LENGTH) {
        onComplete?.(pasted);
      }
    },
    [onChange, onComplete],
  );

  return (
    <div
      className={`flex gap-3 justify-center ${className}`.trim()}
      onPaste={handlePaste}
      role="group"
      aria-label="Código OTP de 6 dígitos"
    >
      {digits.map((digit, i) => (
        <OtpDigitInput
          key={i}
          id={`otp-digit-${i}`}
          index={i}
          value={digit}
          onChange={handleDigitChange}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          hasError={hasError}
          inputRef={makeInputRef(i)}
        />
      ))}
    </div>
  );
}
