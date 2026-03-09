/* c8 ignore start — barrel re-exports contain no testable logic */
/**
 * @fileoverview Atoms barrel export.
 *
 * Re-exports all atom components for convenient importing.
 * Atoms are the smallest UI building blocks with no business logic.
 *
 * @remarks
 * FRONTEND-GUIDELINES.md §3.1 — Atoms.
 * Components added here should only receive props and emit events.
 *
 * @example
 * ```tsx
 * import { Button, TextField } from '@/components/atoms';
 * ```
 */

export { Button } from './Button';
export { type ButtonProps, type ButtonVariant } from './Button';
export { TextField } from './TextField';
export { type TextFieldProps } from './TextField';
export { ErrorMessage } from './ErrorMessage';
export { type ErrorMessageProps } from './ErrorMessage';
export { SuccessMessage } from './SuccessMessage';
export { type SuccessMessageProps } from './SuccessMessage';
/* c8 ignore stop */
