/**
 * Home page — temporary placeholder.
 *
 * @remarks
 * This page will be replaced by HU-FE-01 (Landing page).
 * For now it redirects to the Styleguide to validate HU-FE-00.
 *
 * @returns The home page component.
 */
export default function Home(): React.ReactElement {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-bg-dark p-8">
      <h1 className="text-4xl font-bold text-text-light mb-4">Billetera Virtual</h1>
      <p className="text-text-light/70 mb-8">PoC — Sprint 1</p>
      <a
        href="/styleguide"
        className="rounded-lg bg-primary px-6 py-3 font-semibold text-text-light transition hover:opacity-90"
      >
        Ver Styleguide
      </a>
    </main>
  );
}
