/**
 * Home page — Landing page with hero section and access buttons.
 *
 * @remarks
 * HU-FE-01: Landing page with "Ingresar" and "Registrarse" CTAs.
 * FRONTEND-GUIDELINES.md §3.5 — Pages: assemble templates/organisms, no logic.
 *
 * @returns The landing page component.
 */

import { HeroSection } from '@/components/organisms';

export default function Home(): React.ReactElement {
  return <HeroSection />;
}
