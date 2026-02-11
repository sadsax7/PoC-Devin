# PoC Monorepo

Monorepo con Backend (Python + Poetry) y Frontend (Next.js)

## Estructura del Proyecto

```
.
├── backend/          # API Backend con arquitectura hexagonal
├── frontend/         # Aplicación Next.js con atomic design
└── README.md
```

## Backend

- **Gestión de paquetes:** Poetry
- **Arquitectura:** Hexagonal (Ports & Adapters)
- **Estructura:**
  - `application/` - Casos de uso
  - `domain/` - Entidades y reglas de negocio
  - `infrastructure/` - Adaptadores e implementaciones

### Configurar Backend

```bash
cd backend
poetry install
poetry run python main.py
```

## Frontend

- **Framework:** Next.js
- **Arquitectura:** Atomic Design
- **Estructura:**
  - `atoms/` - Componentes básicos
  - `molecules/` - Combinación de átomos
  - `organisms/` - Componentes complejos
  - `templates/` - Plantillas de páginas
  - `pages/` - Páginas de la aplicación

### Configurar Frontend

```bash
cd frontend
npm install
npm run dev
```
