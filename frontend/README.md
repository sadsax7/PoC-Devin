# Frontend — Billetera Virtual PoC

> Next.js 16 + Tailwind CSS 3 + Atomic Design + TypeScript Strict

## Estructura

```
frontend/
├── src/
│   ├── app/                  # App Router (Next.js)
│   │   ├── layout.tsx        # Root layout (Inter, dark mode)
│   │   ├── page.tsx          # Home placeholder
│   │   └── styleguide/       # Styleguide page
│   ├── components/           # Atomic Design
│   │   ├── atoms/            # Componentes base (Button, Input, …)
│   │   ├── molecules/        # Combinaciones (SearchBar, FormField, …)
│   │   ├── organisms/        # Complejos (Header, UserList, …)
│   │   └── templates/        # Layouts de página
│   ├── styles/
│   │   ├── globals.css       # Tailwind layers + Inter import + dark
│   │   └── design-tokens.ts  # Tokens programáticos
│   └── utils/                # Helpers
├── tests/
│   ├── setup.ts              # jsdom env para Mocha
│   └── unit/
│       ├── design-tokens.spec.ts   # 15 tests
│       └── tailwind-config.spec.ts # 7 tests
├── .mocharc.json             # Mocha + tsx config
├── tailwind.config.js        # Tokens + dark mode
├── tsconfig.json             # Strict mode + path aliases
├── eslint.config.mjs         # Flat config + Prettier
└── package.json
```

## Requisitos

- Node.js >= 20
- npm >= 10

## Instalación

```bash
npm install
```

## Desarrollo

```bash
npm run dev
```

Abrir [http://localhost:3000](http://localhost:3000) — Home page  
Abrir [http://localhost:3000/styleguide](http://localhost:3000/styleguide) — Design System

## Quality Gates

```bash
npm run lint          # ESLint (next + prettier + sonarjs + unused-imports)
npm run type-check    # TypeScript strict (tsc --noEmit)
npm test              # Mocha — 22 tests
npm run test:coverage # c8 + Mocha — umbral ≥ 85%
npx prettier --check "src/**/*.{ts,tsx}"  # Formatting
```

## Design System

| Token        | Valor     | Uso                      |
|-------------|-----------|--------------------------|
| `primary`   | `#FF6B00` | Naranja institucional    |
| `bg-dark`   | `#000000` | Fondo modo oscuro        |
| `text-light`| `#FFFFFF` | Texto sobre fondo oscuro |
| Font        | Inter     | Google Fonts (300-700)   |

Dark mode: estrategia `class` en `<html>`.

## Atomic Design

- **Atoms:** Componentes base e indivisibles (Button, Input, Label)
- **Molecules:** Combinación de átomos (SearchBar, FormField)
- **Organisms:** Componentes complejos (Header, UserList, ProductGrid)
- **Templates:** Layouts de página sin contenido específico
