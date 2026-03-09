/* c8 ignore start — barrel re-exports contain no testable logic */
/**
 * @fileoverview Molecules barrel export.
 *
 * Re-exports all molecule components.
 * Molecules group atoms for focused UI roles (e.g., FormField, OtpCodeInput).
 *
 * @remarks
 * FRONTEND-GUIDELINES.md §3.2 — Molecules.
 * May contain lightweight UI validations but no business logic.
 *
 * @example
 * ```tsx
 * import { FormField, OtpCodeInput } from '@/components/molecules';
 * ```
 */

export { FormField } from './FormField';
export { type FormFieldProps } from './FormField';
export { PasswordStrengthIndicator, calculateStrength } from './PasswordStrengthIndicator';
export {
  type PasswordStrengthIndicatorProps,
  type PasswordStrength,
} from './PasswordStrengthIndicator';
/* c8 ignore stop */
