/**
 * Registration page — renders the RegisterForm organism.
 *
 * @remarks
 * HU-FE-02: Acceptance Criteria #5 (Atomic Design — Pages).
 * FRONTEND-GUIDELINES.md §3.5 — Pages: assemble templates/organisms, no logic.
 *
 * @returns The registration page component.
 */

'use client';

import { RegisterForm } from '@/components/organisms';

export default function RegisterPage(): React.ReactElement {
  return <RegisterForm />;
}
