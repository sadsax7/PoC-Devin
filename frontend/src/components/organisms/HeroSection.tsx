/**
 * @fileoverview HeroSection organism.
 *
 * Landing-page hero that displays the app logo, welcome title,
 * subtitle, and two call-to-action buttons ("Ingresar" / "Registrarse").
 *
 * @remarks
 * HU-FE-01: Acceptance Criteria #1 (hero), #2 (CTA), #4 (responsive),
 *           #5 (Atomic Design), #6 (navigation), #7 (accessibility).
 * FRONTEND-GUIDELINES.md §3.3 — Organisms.
 *
 * @example
 * ```tsx
 * import { HeroSection } from '@/components/organisms';
 *
 * <HeroSection />
 * ```
 */

import React from 'react';
import { Button } from '@/components/atoms';

/**
 * Props for the {@link HeroSection} component.
 */
export interface HeroSectionProps {
  /** Override the hero title. @defaultValue `'Bienvenido a Billetera Virtual'` */
  title?: string;

  /** Override the hero subtitle. @defaultValue `'Tu dinero seguro, rápido y fácil de usar'` */
  subtitle?: string;

  /** Path to the logo image. @defaultValue `'/next.svg'` */
  logoSrc?: string;

  /** Alt text for the logo. @defaultValue `'Billetera Virtual logo'` */
  logoAlt?: string;

  /** Navigation target for the "Ingresar" button. @defaultValue `'/auth/login'` */
  loginHref?: string;

  /** Navigation target for the "Registrarse" button. @defaultValue `'/auth/register'` */
  registerHref?: string;

  /** Additional CSS classes for the root container. */
  className?: string;
}

/**
 * HeroSection organism — landing-page hero with CTA buttons.
 *
 * Renders a vertically-centered hero on mobile (flex-col) and a
 * horizontally-spaced layout on desktop (md: breakpoint).
 *
 * @param props - {@link HeroSectionProps}
 * @returns A responsive hero section element.
 */
export function HeroSection({
  title = 'Bienvenido a Billetera Virtual',
  subtitle = 'Tu dinero seguro, rápido y fácil de usar',
  logoSrc = '/next.svg',
  logoAlt = 'Billetera Virtual logo',
  loginHref = '/auth/login',
  registerHref = '/auth/register',
  className = '',
}: HeroSectionProps): React.ReactElement {
  return (
    <section
      className={`flex min-h-screen flex-col items-center justify-center bg-bg-dark px-6 py-12 text-center ${className}`.trim()}
      aria-label="Hero section"
    >
      {/* Logo — placeholder until billetera logo is available (AC #1) */}
      {/* eslint-disable-next-line @next/next/no-img-element -- placeholder logo, will migrate to next/image */}
      <img
        src={logoSrc}
        alt={logoAlt}
        className="mb-8 h-16 w-auto md:h-20"
        width={120}
        height={80}
      />

      {/* Title */}
      <h1 className="mb-4 text-3xl font-bold text-text-light md:text-5xl">{title}</h1>

      {/* Subtitle */}
      <p className="mb-10 max-w-md text-lg text-text-light/70 md:text-xl">{subtitle}</p>

      {/* CTA buttons — stacked on mobile, row on desktop */}
      <div
        className="flex w-full max-w-sm flex-col gap-4 md:max-w-md md:flex-row md:gap-6"
        role="group"
        aria-label="Opciones de acceso"
      >
        <Button variant="outline" href={loginHref} className="w-full">
          Ingresar
        </Button>
        <Button variant="solid" href={registerHref} className="w-full">
          Registrarse
        </Button>
      </div>
    </section>
  );
}
