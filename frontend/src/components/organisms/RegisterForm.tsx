/**
 * @fileoverview RegisterForm organism component.
 *
 * Full registration form with real-time validation, password strength
 * indicator, backend integration, and accessible feedback messages.
 *
 * @remarks
 * HU-FE-02: Acceptance Criteria #1-#8.
 * FRONTEND-GUIDELINES.md §3.3 — Organisms.
 *
 * @example
 * ```tsx
 * import { RegisterForm } from '@/components/organisms';
 *
 * <RegisterForm />
 * ```
 */

import React, { useCallback, useMemo, useState } from 'react';
import { Button, SuccessMessage, ErrorMessage } from '@/components/atoms';
import { FormField, PasswordStrengthIndicator } from '@/components/molecules';
import { useRegister, type RegisterFormData } from '@/lib/auth/useRegister';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

/** Internal form field values. */
export interface RegisterFormValues {
  /** Phone number in E.164 format. */
  phone: string;
  /** User password. */
  password: string;
  /** Confirmation password (must match). */
  confirmPassword: string;
  /** Optional email address. */
  email: string;
  /** Optional display name. */
  name: string;
}

/** Per-field validation error strings. */
export interface RegisterFormErrors {
  /** Phone validation error. */
  phone: string;
  /** Password validation error. */
  password: string;
  /** Confirm-password mismatch error. */
  confirmPassword: string;
  /** Email format error. */
  email: string;
  /** Name validation error. */
  name: string;
}

/**
 * Props for the {@link RegisterForm} component.
 */
export interface RegisterFormProps {
  /** Additional CSS classes for the root wrapper. */
  className?: string;
  /** Path to the logo image. @defaultValue `'/next.svg'` */
  logoSrc?: string;
  /** Alt text for the logo. @defaultValue `'Billetera Virtual logo'` */
  logoAlt?: string;
  /** Override navigation function (useful for testing). */
  navigateFn?: (path: string) => void;
}

// ---------------------------------------------------------------------------
// Validation helpers
// ---------------------------------------------------------------------------

/** E.164 phone regex: + followed by 7-15 digits. */
const E164_REGEX = /^\+\d{7,15}$/;

/** Basic email regex per HU-FE-02 AC #2. */
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * Validate a phone number in E.164 format.
 *
 * @param value - Phone string to validate.
 * @returns Error message or empty string.
 */
export function validatePhone(value: string): string {
  if (!value) return 'El teléfono es obligatorio.';
  if (!E164_REGEX.test(value)) {
    return 'Formato de teléfono inválido. Usa +[código país][número]';
  }
  return '';
}

/**
 * Validate a password against required rules.
 *
 * @param value - Password string to validate.
 * @returns Error message or empty string.
 */
export function validatePassword(value: string): string {
  if (!value) return 'La contraseña es obligatoria.';
  if (value.length < 8) return 'Mínimo 8 caracteres.';
  if (value.length > 128) return 'Máximo 128 caracteres.';
  if (!/[A-Z]/.test(value)) return 'Debe contener al menos 1 mayúscula.';
  if (!/[a-z]/.test(value)) return 'Debe contener al menos 1 minúscula.';
  if (!/\d/.test(value)) return 'Debe contener al menos 1 número.';
  if (!/[^A-Za-z0-9]/.test(value)) return 'Debe contener al menos 1 carácter especial.';
  return '';
}

/**
 * Validate that password confirmation matches.
 *
 * @param password - Original password.
 * @param confirm - Confirmation value.
 * @returns Error message or empty string.
 */
export function validateConfirmPassword(password: string, confirm: string): string {
  if (!confirm) return 'Confirma tu contraseña.';
  if (password !== confirm) return 'Las contraseñas no coinciden';
  return '';
}

/**
 * Validate an optional email address.
 *
 * @param value - Email string (may be empty).
 * @returns Error message or empty string.
 */
export function validateEmail(value: string): string {
  if (!value) return '';
  if (value.length > 255) return 'Máximo 255 caracteres.';
  if (!EMAIL_REGEX.test(value)) return 'Formato de email inválido.';
  return '';
}

/**
 * Validate an optional name field.
 *
 * @param value - Name string (may be empty).
 * @returns Error message or empty string.
 */
export function validateName(value: string): string {
  if (value.length > 100) return 'Máximo 100 caracteres.';
  return '';
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const INITIAL_VALUES: RegisterFormValues = {
  phone: '',
  password: '',
  confirmPassword: '',
  email: '',
  name: '',
};

const INITIAL_ERRORS: RegisterFormErrors = {
  phone: '',
  password: '',
  confirmPassword: '',
  email: '',
  name: '',
};

// ---------------------------------------------------------------------------
// Validation dispatch map
// ---------------------------------------------------------------------------

/**
 * Map each form field to its validation function.
 *
 * `confirmPassword` needs the current password for comparison, so it
 * receives a second argument via a wrapper in {@link getFieldError}.
 *
 * @internal
 */
const FIELD_VALIDATORS: Record<
  keyof RegisterFormValues,
  (value: string, password?: string) => string
> = {
  phone: (v) => validatePhone(v),
  password: (v) => validatePassword(v),
  confirmPassword: (v, pw) => validateConfirmPassword(pw ?? '', v),
  email: (v) => validateEmail(v),
  name: (v) => validateName(v),
};

/**
 * Resolve a field's validation error using the dispatch map.
 *
 * @param field - The field key to validate.
 * @param value - The current field value.
 * @param password - The current password (needed for confirmPassword).
 * @returns The validation error string (empty when valid).
 * @internal
 */
function getFieldError(field: keyof RegisterFormValues, value: string, password: string): string {
  return FIELD_VALIDATORS[field](value, password);
}

// ---------------------------------------------------------------------------
// Sub-components (extracted to reduce component complexity)
// ---------------------------------------------------------------------------

/** Props for the visibility toggle suffix button. */
interface ToggleSuffixProps {
  /** Current visibility state. */
  visible: boolean;
  /** Toggle handler. */
  onToggle: () => void;
  /** Aria label when hidden. */
  showLabel: string;
  /** Aria label when visible. */
  hideLabel: string;
}

/**
 * Visibility toggle button used as TextField suffix.
 *
 * @param props - {@link ToggleSuffixProps}
 * @returns A toggle button element.
 * @internal
 */
function ToggleSuffix({
  visible,
  onToggle,
  showLabel,
  hideLabel,
}: ToggleSuffixProps): React.ReactElement {
  return (
    <button
      type="button"
      onClick={onToggle}
      className="text-text-light/50 hover:text-text-light"
      aria-label={visible ? hideLabel : showLabel}
    >
      {visible ? '🙈' : '👁'}
    </button>
  );
}

/**
 * Success overlay shown after registration completes.
 *
 * @param props - className for the section wrapper.
 * @returns A success section element.
 * @internal
 */
function SuccessOverlay({ className }: { className: string }): React.ReactElement {
  return (
    <section
      className={`flex min-h-screen flex-col items-center justify-center p-6 bg-bg-dark text-text-light ${className}`.trim()}
      aria-label="Registro exitoso"
    >
      <SuccessMessage message="¡Cuenta creada exitosamente! Redirigiendo..." />
    </section>
  );
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

/**
 * RegisterForm organism — full registration form with validation & feedback.
 *
 * Manages local form state, performs real-time validation, and delegates
 * submission to the {@link useRegister} hook.
 *
 * @param props - {@link RegisterFormProps}
 * @returns A form element or success overlay.
 */
export function RegisterForm({
  className = '',
  logoSrc = '/next.svg',
  logoAlt = 'Billetera Virtual logo',
  navigateFn,
}: RegisterFormProps): React.ReactElement {
  const { register, isLoading, error: apiError, success } = useRegister(navigateFn);

  const [values, setValues] = useState<RegisterFormValues>(INITIAL_VALUES);
  const [errors, setErrors] = useState<RegisterFormErrors>(INITIAL_ERRORS);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  // ---------------------------------------------------------------------------
  // Derived state
  // ---------------------------------------------------------------------------

  /** Whether all required fields pass validation and are non-empty. */
  const isFormValid = useMemo(() => {
    const phoneErr = validatePhone(values.phone);
    const passErr = validatePassword(values.password);
    const confirmErr = validateConfirmPassword(values.password, values.confirmPassword);
    const emailErr = validateEmail(values.email);
    const nameErr = validateName(values.name);
    return !phoneErr && !passErr && !confirmErr && !emailErr && !nameErr;
  }, [values]);

  // ---------------------------------------------------------------------------
  // Handlers
  // ---------------------------------------------------------------------------

  /** Update a single field and revalidate it. */
  const handleChange = useCallback(
    (field: keyof RegisterFormValues) =>
      (e: React.ChangeEvent<HTMLInputElement>): void => {
        const newValue = e.target.value;
        setValues((prev) => ({ ...prev, [field]: newValue }));

        const fieldError = getFieldError(field, newValue, values.password);

        setErrors((prev) => {
          const next = { ...prev, [field]: fieldError };
          // Re-check confirmPassword when password changes
          if (field === 'password' && values.confirmPassword) {
            next.confirmPassword = validateConfirmPassword(newValue, values.confirmPassword);
          }
          return next;
        });
      },
    [values.password, values.confirmPassword],
  );

  /** Submit the form. */
  const handleSubmit = useCallback(
    async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
      e.preventDefault();
      if (!isFormValid || isLoading) return;

      const data: RegisterFormData = {
        phone: values.phone,
        password: values.password,
        ...(values.email ? { email: values.email } : {}),
        ...(values.name ? { name: values.name } : {}),
      };

      await register(data);
    },
    [isFormValid, isLoading, values, register],
  );

  // ---------------------------------------------------------------------------
  // Render helpers
  // ---------------------------------------------------------------------------

  const passwordType = showPassword ? 'text' : 'password';
  const confirmType = showConfirm ? 'text' : 'password';
  const submitDisabled = !isFormValid || isLoading;
  const submitLabel = isLoading ? 'Registrando...' : 'Registrarse';

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  if (success) {
    return <SuccessOverlay className={className} />;
  }

  return (
    <section
      className={`flex min-h-screen flex-col items-center justify-center p-6 bg-bg-dark text-text-light ${className}`.trim()}
      aria-label="Formulario de registro"
    >
      {/* Logo */}
      {/* eslint-disable-next-line @next/next/no-img-element -- placeholder logo */}
      <img
        src={logoSrc}
        alt={logoAlt}
        className="mb-8 h-16 w-auto md:h-20"
        width={120}
        height={80}
      />

      <h1 className="mb-6 text-2xl font-bold">Crear cuenta</h1>

      <form
        onSubmit={handleSubmit}
        noValidate
        className="flex w-full max-w-sm flex-col gap-4"
        aria-label="Formulario de registro"
      >
        {/* Phone */}
        <FormField
          id="phone"
          label="Teléfono"
          placeholder="ej: +573001234567"
          value={values.phone}
          onChange={handleChange('phone')}
          error={errors.phone}
          disabled={isLoading}
          helperText="Formato E.164: +[código país][número]"
        />

        {/* Password */}
        <FormField
          id="password"
          label="Contraseña"
          type={passwordType}
          value={values.password}
          onChange={handleChange('password')}
          error={errors.password}
          disabled={isLoading}
          maxLength={128}
          suffix={
            <ToggleSuffix
              visible={showPassword}
              onToggle={() => setShowPassword((p) => !p)}
              showLabel="Mostrar contraseña"
              hideLabel="Ocultar contraseña"
            />
          }
        />
        <PasswordStrengthIndicator password={values.password} />

        {/* Confirm password */}
        <FormField
          id="confirm_password"
          label="Confirmar contraseña"
          type={confirmType}
          value={values.confirmPassword}
          onChange={handleChange('confirmPassword')}
          error={errors.confirmPassword}
          disabled={isLoading}
          suffix={
            <ToggleSuffix
              visible={showConfirm}
              onToggle={() => setShowConfirm((p) => !p)}
              showLabel="Mostrar confirmación"
              hideLabel="Ocultar confirmación"
            />
          }
        />

        {/* Email (optional) */}
        <FormField
          id="email"
          label="Email (opcional)"
          type="email"
          placeholder="user@example.com"
          value={values.email}
          onChange={handleChange('email')}
          error={errors.email}
          disabled={isLoading}
          maxLength={255}
        />

        {/* Name (optional) */}
        <FormField
          id="name"
          label="Nombre (opcional)"
          placeholder="Juan Pérez"
          value={values.name}
          onChange={handleChange('name')}
          error={errors.name}
          disabled={isLoading}
          maxLength={100}
        />

        {/* API error */}
        <ErrorMessage message={apiError} />

        {/* Submit */}
        <Button
          variant="solid"
          fullWidth
          disabled={submitDisabled}
          ariaBusy={isLoading}
          onClick={undefined}
        >
          {submitLabel}
        </Button>

        {/* Secondary — login link */}
        <p className="text-center text-sm text-text-light/60">
          ¿Ya tienes cuenta?{' '}
          <Button variant="outline" href="/auth/login" className="ml-1 px-3 py-1 text-sm">
            Ingresar
          </Button>
        </p>
      </form>
    </section>
  );
}
