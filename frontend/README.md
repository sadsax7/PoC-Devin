# Frontend - Next.js con Atomic Design

## Estructura

```
frontend/
├── src/
│   ├── components/        # Componentes siguiendo Atomic Design
│   │   ├── atoms/        # Componentes básicos (botones, inputs, etc.)
│   │   ├── molecules/    # Combinación de átomos (formularios simples, cards, etc.)
│   │   ├── organisms/    # Componentes complejos (header, footer, secciones)
│   │   ├── templates/    # Plantillas de páginas
│   │   └── pages/        # Páginas específicas (opcional)
│   ├── app/              # App Router de Next.js
│   ├── styles/           # Estilos globales
│   └── utils/            # Utilidades y helpers
├── public/               # Archivos estáticos
├── package.json
└── next.config.js
```

## Atomic Design

- **Atoms:** Componentes básicos e indivisibles (Button, Input, Label)
- **Molecules:** Combinación de átomos (SearchBar, FormField)
- **Organisms:** Componentes complejos (Header, UserList, ProductGrid)
- **Templates:** Layouts de páginas sin contenido específico
- **Pages:** Instancias de templates con contenido real

## Instalación

```bash
npm install
```

## Ejecución

```bash
npm run dev
```

Abrir [http://localhost:3000](http://localhost:3000) en el navegador.

## Build

```bash
npm run build
npm start
```
