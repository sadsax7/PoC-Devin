/**
 * @fileoverview Design tokens for the Billetera Virtual PoC.
 *
 * Central registry of design tokens used across the application.
 * These values mirror the Tailwind config and serve as the single
 * source of truth for programmatic access to design values.
 *
 * @remarks
 * HU-FE-00: Acceptance Criteria #2 — Design tokens.
 * FRONTEND-GUIDELINES.md §5.3 — Design Tokens & Theming.
 */

/** Color tokens matching tailwind.config.js */
export const colors = {
  /** Primary brand color — institutional orange */
  primary: '#FF6B00',
  /** Dark background */
  bgDark: '#000000',
  /** Light text on dark backgrounds */
  textLight: '#FFFFFF',
};

/** Font family tokens */
export const fonts = {
  /** Primary font — Inter from Google Fonts */
  sans: 'Inter, ui-sans-serif, system-ui, sans-serif',
};

/** Font weight tokens */
export const fontWeights = {
  light: 300,
  regular: 400,
  medium: 500,
  semibold: 600,
  bold: 700,
};

/** Spacing scale (in px, matching Tailwind defaults) */
export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  '2xl': '48px',
};

/** Border radius tokens */
export const radii = {
  sm: '4px',
  md: '8px',
  lg: '12px',
  full: '9999px',
};

/** All design tokens consolidated */
export const designTokens = {
  colors,
  fonts,
  fontWeights,
  spacing,
  radii,
};
