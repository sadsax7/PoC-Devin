/**
 * Styleguide page — HU-FE-00 Acceptance Criteria #4 (DoD #7).
 *
 * Displays the institutional design system: typography, color palette,
 * spacing, and dark mode preview.
 *
 * @remarks
 * This page serves as a living reference for designers and developers
 * to verify visual consistency before building components.
 */
import { colors, fonts, fontWeights, spacing, radii } from '@/styles/design-tokens';

/** Color swatch data for rendering the palette */
const colorSwatches = [
  { name: 'Primary', value: colors.primary, textClass: 'text-text-light' },
  { name: 'Background Dark', value: colors.bgDark, textClass: 'text-text-light' },
  { name: 'Text Light', value: colors.textLight, textClass: 'text-black' },
];

/**
 * Styleguide page component.
 *
 * @returns The Styleguide page with design token previews.
 */
export default function StyleguidePage(): React.ReactElement {
  return (
    <main className="min-h-screen bg-white p-8 dark:bg-bg-dark">
      {/* Header */}
      <header className="mb-12">
        <h1 className="text-4xl font-bold text-black dark:text-text-light">
          🎨 Design System — Billetera Virtual
        </h1>
        <p className="mt-2 text-lg text-black/60 dark:text-text-light/60">
          Tokens institucionales definidos en HU-FE-00
        </p>
      </header>

      {/* Typography */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold text-black dark:text-text-light">
          Tipografía — Inter
        </h2>
        <p className="mb-2 text-sm text-black/50 dark:text-text-light/50">
          Font family: {fonts.sans}
        </p>
        <div className="space-y-3 rounded-lg border border-black/10 p-6 dark:border-text-light/10">
          <p style={{ fontWeight: fontWeights.light }} className="text-black dark:text-text-light">
            Light (300) — The quick brown fox jumps over the lazy dog
          </p>
          <p
            style={{ fontWeight: fontWeights.regular }}
            className="text-black dark:text-text-light"
          >
            Regular (400) — The quick brown fox jumps over the lazy dog
          </p>
          <p style={{ fontWeight: fontWeights.medium }} className="text-black dark:text-text-light">
            Medium (500) — The quick brown fox jumps over the lazy dog
          </p>
          <p
            style={{ fontWeight: fontWeights.semibold }}
            className="text-black dark:text-text-light"
          >
            Semibold (600) — The quick brown fox jumps over the lazy dog
          </p>
          <p style={{ fontWeight: fontWeights.bold }} className="text-black dark:text-text-light">
            Bold (700) — The quick brown fox jumps over the lazy dog
          </p>
        </div>
      </section>

      {/* Color Palette */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold text-black dark:text-text-light">
          Paleta de Colores
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {colorSwatches.map((swatch) => (
            <div
              key={swatch.name}
              className="flex flex-col items-center rounded-lg border border-black/10 p-6 dark:border-text-light/10"
              style={{ backgroundColor: swatch.value }}
            >
              <span className={`text-lg font-semibold ${swatch.textClass}`}>{swatch.name}</span>
              <span className={`text-sm ${swatch.textClass} opacity-70`}>{swatch.value}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Spacing */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold text-black dark:text-text-light">Espaciado</h2>
        <div className="space-y-2">
          {Object.entries(spacing).map(([name, value]) => (
            <div key={name} className="flex items-center gap-4">
              <span className="w-12 text-sm text-black/60 dark:text-text-light/60">{name}</span>
              <div className="h-4 rounded bg-primary" style={{ width: value }} />
              <span className="text-sm text-black/40 dark:text-text-light/40">{value}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Border Radius */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold text-black dark:text-text-light">
          Border Radius
        </h2>
        <div className="flex flex-wrap gap-4">
          {Object.entries(radii).map(([name, value]) => (
            <div key={name} className="flex flex-col items-center gap-2">
              <div
                className="h-16 w-16 bg-primary"
                style={{ borderRadius: value }}
                title={`${name}: ${value}`}
              />
              <span className="text-xs text-black/60 dark:text-text-light/60">
                {name} ({value})
              </span>
            </div>
          ))}
        </div>
      </section>

      {/* Dark Mode Preview */}
      <section className="mb-12">
        <h2 className="mb-4 text-2xl font-semibold text-black dark:text-text-light">
          Dark Mode — Inversión Total
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {/* Light card */}
          <div className="rounded-lg bg-white p-6 shadow-md">
            <h3 className="text-lg font-semibold text-black">Light Mode</h3>
            <p className="mt-2 text-black/70">Fondo blanco, texto negro, accent naranja.</p>
            <button className="mt-4 rounded-lg bg-primary px-4 py-2 font-semibold text-text-light">
              Botón Primario
            </button>
          </div>
          {/* Dark card */}
          <div className="rounded-lg bg-bg-dark p-6 shadow-md">
            <h3 className="text-lg font-semibold text-text-light">Dark Mode</h3>
            <p className="mt-2 text-text-light/70">Fondo negro, texto blanco, accent naranja.</p>
            <button className="mt-4 rounded-lg bg-primary px-4 py-2 font-semibold text-text-light">
              Botón Primario
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-black/10 pt-4 text-sm text-black/40 dark:border-text-light/10 dark:text-text-light/40">
        Billetera Virtual PoC — HU-FE-00 Styleguide — Sprint 1
      </footer>
    </main>
  );
}
