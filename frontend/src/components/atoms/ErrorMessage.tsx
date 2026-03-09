/**
 * @fileoverview ErrorMessage atom component.
 *
 * Displays an error message with an optional X icon in red.
 * Used for form-level and API error feedback.
 *
 * @remarks
 * HU-FE-02: Acceptance Criteria #3 (error state), #7 (accessibility).
 * FRONTEND-GUIDELINES.md §3.1 — Atoms.
 *
 * @example
 * ```tsx
 * import { ErrorMessage } from '@/components/atoms';
 *
 * <ErrorMessage message="Este teléfono ya está registrado." />
 * ```
 */

import React from 'react';

/**
 * Props for the {@link ErrorMessage} component.
 */
export interface ErrorMessageProps {
  /** The error text to display. When empty/undefined, nothing renders. */
  message?: string;

  /** Whether to show the X icon before the message. @defaultValue `true` */
  showIcon?: boolean;

  /** Additional CSS classes for the root element. */
  className?: string;
}

/**
 * ErrorMessage atom — renders a red error message with optional X icon.
 *
 * Returns `null` when `message` is falsy, avoiding empty DOM nodes.
 *
 * @param props - {@link ErrorMessageProps}
 * @returns An error paragraph or null.
 */
export function ErrorMessage({
  message,
  showIcon = true,
  className = '',
}: ErrorMessageProps): React.ReactElement | null {
  if (!message) {
    return null;
  }

  return (
    <p
      role="alert"
      aria-live="polite"
      className={`flex items-center gap-2 text-sm text-red-500 ${className}`.trim()}
    >
      {showIcon && <span aria-hidden="true">✕</span>}
      {message}
    </p>
  );
}
