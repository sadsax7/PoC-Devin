/* c8 ignore start — barrel re-exports contain no testable logic */
/**
 * @fileoverview Organisms barrel export.
 *
 * Re-exports all organism components.
 * Organisms combine molecules into functional structures (e.g., LoginForm).
 *
 * @remarks
 * FRONTEND-GUIDELINES.md §3.3 — Organisms.
 * Organisms invoke domain hooks from `lib/` and manage local form state.
 *
 * @example
 * ```tsx
 * import { LoginForm, RegisterForm } from '@/components/organisms';
 * ```
 */

export { HeroSection, type HeroSectionProps } from './HeroSection';
export { RegisterForm } from './RegisterForm';
export {
  type RegisterFormProps,
  type RegisterFormValues,
  type RegisterFormErrors,
} from './RegisterForm';
/* c8 ignore stop */
