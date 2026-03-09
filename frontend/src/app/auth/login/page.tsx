/**
 * Login page — renders the full authentication flow via LoginFlowManager.
 *
 * @remarks
 * HU-FE-03: Acceptance Criteria #5 (Atomic Design — Pages), #6 (routing).
 * FRONTEND-GUIDELINES.md §3.5 — Pages: assemble organisms, no business logic.
 *
 * @returns The login page component.
 */

'use client';

import React from 'react';
import { LoginFlowManager } from '@/components/organisms';

/**
 * LoginPage — entry point for `/auth/login`.
 *
 * Delegates all logic to {@link LoginFlowManager} which handles
 * the two-step Login → MFA flow without changing the URL.
 *
 * @returns The login flow page element.
 */
export default function LoginPage(): React.ReactElement {
  return <LoginFlowManager />;
}
