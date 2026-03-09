/**
 * @fileoverview Button atom component.
 *
 * A reusable button component supporting "solid" and "outline" variants.
 * Uses the institutional primary color (`--primary` / `#FF6B00`).
 *
 * @remarks
 * HU-FE-01: Acceptance Criteria #2, #3.
 * FRONTEND-GUIDELINES.md §3.1 — Atoms: no business logic, only props + events.
 *
 * @example
 * ```tsx
 * import { Button } from '@/components/atoms';
 *
 * <Button variant="solid" href="/auth/register">Registrarse</Button>
 * <Button variant="outline" href="/auth/login">Ingresar</Button>
 * ```
 */

import React from 'react';

/**
 * Visual variant for the Button component.
 *
 * - `solid`: filled background with primary color, white text.
 * - `outline`: transparent background with primary-color border and text.
 */
export type ButtonVariant = 'solid' | 'outline';

/**
 * Props for the {@link Button} component.
 */
export interface ButtonProps {
  /** Visual style variant. @defaultValue `'solid'` */
  variant?: ButtonVariant;

  /** Content rendered inside the button. */
  children?: React.ReactNode;

  /**
   * When provided, the button renders as an `<a>` tag for client-side
   * navigation (should be wrapped with Next.js `<Link>` by consumers).
   */
  href?: string;

  /** Whether the button is disabled. */
  disabled?: boolean;

  /** Click handler (only when `href` is not provided). */
  onClick?: React.MouseEventHandler<HTMLButtonElement | HTMLAnchorElement>;

  /** Additional CSS classes appended to the base styles. */
  className?: string;

  /** Accessible label when visual text is insufficient. */
  ariaLabel?: string;

  /** Whether the button should stretch to full container width. */
  fullWidth?: boolean;

  /** Indicates the button is busy (e.g. form submitting). */
  ariaBusy?: boolean;
}

/**
 * Base CSS classes shared by both variants.
 * @internal
 */
const BASE_CLASSES =
  'inline-flex items-center justify-center rounded-lg px-6 py-3 font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary';

/**
 * Variant-specific CSS class map.
 * @internal
 */
const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  solid:
    'bg-primary text-white hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed',
  outline:
    'border-2 border-primary text-primary bg-transparent hover:bg-primary/10 disabled:opacity-50 disabled:cursor-not-allowed',
};

/**
 * Button atom — renders either a `<button>` or `<a>` element.
 *
 * When `href` is provided the component renders an anchor `<a>`.
 * Otherwise it renders a standard `<button>`.
 *
 * @param props - {@link ButtonProps}
 * @returns A styled button or anchor element.
 */
export function Button({
  variant = 'solid',
  children,
  href,
  disabled = false,
  onClick,
  className = '',
  ariaLabel,
  fullWidth = false,
  ariaBusy,
}: ButtonProps): React.ReactElement {
  const widthClass = fullWidth ? 'w-full' : '';
  const classes = `${BASE_CLASSES} ${VARIANT_CLASSES[variant]} ${widthClass} ${className}`.trim();

  if (href && !disabled) {
    return (
      <a
        href={href}
        className={classes}
        onClick={onClick}
        aria-label={ariaLabel}
        aria-busy={ariaBusy}
        role="link"
      >
        {children}
      </a>
    );
  }

  return (
    <button
      type="button"
      className={classes}
      disabled={disabled}
      onClick={onClick}
      aria-label={ariaLabel}
      aria-busy={ariaBusy}
    >
      {children}
    </button>
  );
}
