/**
 * @fileoverview SuccessMessage atom component.
 *
 * Displays a success message with an optional checkmark icon in green.
 * Used for form submission success feedback.
 *
 * @remarks
 * HU-FE-02: Acceptance Criteria #3 (success state).
 * FRONTEND-GUIDELINES.md §3.1 — Atoms.
 *
 * @example
 * ```tsx
 * import { SuccessMessage } from '@/components/atoms';
 *
 * <SuccessMessage message="¡Cuenta creada exitosamente!" />
 * ```
 */

import React from 'react';

/**
 * Props for the {@link SuccessMessage} component.
 */
export interface SuccessMessageProps {
  /** The success text to display. When empty/undefined, nothing renders. */
  message?: string;

  /** Whether to show the checkmark icon before the message. @defaultValue `true` */
  showIcon?: boolean;

  /** Additional CSS classes for the root element. */
  className?: string;
}

/**
 * SuccessMessage atom — renders a green success message with optional checkmark.
 *
 * Returns `null` when `message` is falsy, avoiding empty DOM nodes.
 *
 * @param props - {@link SuccessMessageProps}
 * @returns A success paragraph or null.
 */
export function SuccessMessage({
  message,
  showIcon = true,
  className = '',
}: SuccessMessageProps): React.ReactElement | null {
  if (!message) {
    return null;
  }

  return (
    <p
      role="status"
      aria-live="polite"
      className={`flex items-center gap-2 text-sm text-green-500 ${className}`.trim()}
    >
      {showIcon && <span aria-hidden="true">✓</span>}
      {message}
    </p>
  );
}
