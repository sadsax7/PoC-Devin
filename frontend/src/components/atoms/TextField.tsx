/**
 * @fileoverview TextField atom component.
 *
 * A reusable text input with label, error display, and optional suffix icon.
 * Supports `text`, `email`, and `password` input types.
 *
 * @remarks
 * HU-FE-02: Acceptance Criteria #1 (form fields), #7 (accessibility).
 * FRONTEND-GUIDELINES.md §3.1 — Atoms: no business logic, only props + events.
 *
 * @example
 * ```tsx
 * import { TextField } from '@/components/atoms';
 *
 * <TextField
 *   id="phone"
 *   label="Teléfono"
 *   placeholder="ej: +573001234567"
 *   value={phone}
 *   onChange={(e) => setPhone(e.target.value)}
 *   error="Formato inválido"
 * />
 * ```
 */

import React from 'react';

/**
 * Props for the {@link TextField} component.
 */
export interface TextFieldProps {
  /** Unique identifier; also used for label `htmlFor` binding. */
  id: string;

  /** Label text displayed above the input. */
  label: string;

  /** HTML input type. @defaultValue `'text'` */
  type?: 'text' | 'email' | 'password';

  /** Placeholder text shown when input is empty. */
  placeholder?: string;

  /** Controlled input value. */
  value?: string;

  /** Change handler fired on every keystroke. */
  onChange?: React.ChangeEventHandler<HTMLInputElement>;

  /** Error message shown below the input. Empty string hides the message. */
  error?: string;

  /** Whether the input is disabled. */
  disabled?: boolean;

  /** Maximum character length. */
  maxLength?: number;

  /** Optional suffix element (e.g. visibility toggle icon). */
  suffix?: React.ReactNode;

  /** Additional CSS classes for the root wrapper. */
  className?: string;

  /** Accessible description for assistive technologies. */
  ariaDescribedBy?: string;
}

/**
 * TextField atom — renders an input with a label, optional error, and suffix.
 *
 * The label is automatically linked to the input via `htmlFor` / `id`.
 * Error messages render with `role="alert"` and `aria-live="polite"`.
 *
 * @param props - {@link TextFieldProps}
 * @returns A styled text field element.
 */
export function TextField({
  id,
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  disabled = false,
  maxLength,
  suffix,
  className = '',
  ariaDescribedBy,
}: TextFieldProps): React.ReactElement {
  const errorId = `${id}-error`;
  const hasError = Boolean(error);

  return (
    <div className={`flex flex-col gap-1 ${className}`.trim()}>
      <label htmlFor={id} className="text-sm font-medium text-text-light">
        {label}
      </label>
      <div className="relative">
        <input
          id={id}
          name={id}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          disabled={disabled}
          maxLength={maxLength}
          aria-invalid={hasError}
          aria-describedby={hasError ? errorId : ariaDescribedBy}
          className={`w-full rounded-lg border px-4 py-3 text-sm transition-colors
            bg-white/10 text-text-light placeholder:text-text-light/40
            focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary
            disabled:opacity-50 disabled:cursor-not-allowed
            ${hasError ? 'border-red-500' : 'border-white/20 focus:border-primary'}`}
        />
        {suffix && <span className="absolute right-3 top-1/2 -translate-y-1/2">{suffix}</span>}
      </div>
      {hasError && (
        <p id={errorId} role="alert" aria-live="polite" className="text-xs text-red-500">
          {error}
        </p>
      )}
    </div>
  );
}
