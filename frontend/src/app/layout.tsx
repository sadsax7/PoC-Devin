import type { Metadata } from 'next';
import '@/styles/globals.css';

/**
 * Root metadata for the Billetera Virtual PoC.
 *
 * @remarks
 * HU-FE-00: Configures Inter as the global font and sets base metadata.
 */
export const metadata: Metadata = {
  title: 'Billetera Virtual',
  description: 'PoC — Billetera Virtual con Next.js, Tailwind y Atomic Design',
};

/**
 * Root layout component.
 *
 * @remarks
 * - Sets `lang="es"` for Spanish-speaking users.
 * - Applies `font-sans` (Inter) as the base font class.
 * - Supports dark mode via `class` strategy on `<html>`.
 *
 * @param props - Layout props with children.
 * @returns The root HTML structure wrapping all pages.
 */
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  return (
    <html lang="es" suppressHydrationWarning>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
