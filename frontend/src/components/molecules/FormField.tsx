/**
 * @fileoverview FormField molecule component.
 *
 * Groups a {@link TextField} atom with contextual helper text. Serves as
 * the standard form field wrapper across all forms in the application.
 *
 * @remarks
 * HU-FE-02: Acceptance Criteria #1 (form structure), #2 (real-time validation).
 * FRONTEND-GUIDELINES.md §3.2 — Molecules.
 *
 * @example
 * ```tsx
 * import { FormField } from '@/components/molecules';
 *
 * <FormField
 *   id="phone"
 *   label="Teléfono"
 *   placeholder="ej: +573001234567"
 *   value={phone}
 *   onChange={handleChange}
 *   error={phoneError}
 *   helperText="Formato E.164: +[código país][número]"
 * />
 * ```
 */

import React from 'react';
import { TextField } from '@/components/atoms';

/**
 * Props for the {@link FormField} component.
 */
export interface FormFieldProps {
  /** Unique identifier forwarded to the input and label. */
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

  /** Error message shown below the input. */
  error?: string;

  /** Whether the input is disabled. */
  disabled?: boolean;

  /** Maximum character length. */
  maxLength?: number;

  /** Optional suffix element (e.g. eye icon for password toggle). */
  suffix?: React.ReactNode;

  /** Optional helper text displayed below the input when no error. */
  helperText?: string;

  /** Additional CSS classes for the root wrapper. */
  className?: string;
}

/**
 * FormField molecule — wraps a TextField with optional helper text.
 *
 * Error messages take priority over helper text. Only one is shown at a time.
 *
 * @param props - {@link FormFieldProps}
 * @returns A form field element with label, input, error/helper.
 */
export function FormField({
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
  helperText,
  className = '',
}: FormFieldProps): React.ReactElement {
  const helperId = `${id}-helper`;

  return (
    <div className={`flex flex-col gap-1 ${className}`.trim()}>
      <TextField
        id={id}
        label={label}
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        error={error}
        disabled={disabled}
        maxLength={maxLength}
        suffix={suffix}
        ariaDescribedBy={!error && helperText ? helperId : undefined}
      />
      {!error && helperText && (
        <p id={helperId} className="text-xs text-text-light/50">
          {helperText}
        </p>
      )}
    </div>
  );
}
