# Monorepo - PoC Devin

Este es un monorepo completo con backend y frontend configurado y listo para comenzar a desarrollar.

## 📁 Estructura del Proyecto

```
poc-devin/
├── backend/                    # Backend con Python + Poetry
│   ├── domain/                # Capa de dominio (entidades, value objects)
│   ├── application/           # Capa de aplicación (casos de uso)
│   ├── infrastructure/        # Capa de infraestructura (API, persistencia)
│   ├── main.py               # Punto de entrada
│   ├── pyproject.toml        # Configuración de Poetry
│   └── poetry.lock           # Lock file de dependencias
│
├── frontend/                  # Frontend con Next.js + TypeScript
│   ├── src/
│   │   ├── components/       # Componentes con Atomic Design
│   │   │   ├── atoms/       # Componentes básicos
│   │   │   ├── molecules/   # Combinación de átomos
│   │   │   ├── organisms/   # Componentes complejos
│   │   │   └── templates/   # Plantillas de páginas
│   │   ├── app/             # App Router de Next.js
│   │   ├── styles/          # Estilos globales
│   │   └── utils/           # Utilidades
│   ├── package.json
│   └── package-lock.json
│
├── .gitignore
└── README.md
```

## 🚀 Inicio Rápido

### Backend

1. **Instalar dependencias:**
   ```bash
   cd backend
   poetry install
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   ```

3. **Ejecutar el servidor:**
   ```bash
   poetry run python main.py
   ```

   El backend estará disponible en: http://localhost:8000

4. **Documentación de la API:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Frontend

1. **Instalar dependencias:**
   ```bash
   cd frontend
   npm install
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.local.example .env.local
   ```

3. **Ejecutar en modo desarrollo:**
   ```bash
   npm run dev
   ```

   El frontend estará disponible en: http://localhost:3000

4. **Build para producción:**
   ```bash
   npm run build
   npm start
   ```

## 🏗️ Arquitectura

### Backend - Arquitectura Hexagonal

La arquitectura hexagonal (Ports & Adapters) separa las preocupaciones en tres capas:

- **Domain:** Lógica de negocio pura, entidades y reglas
- **Application:** Casos de uso y puertos (interfaces)
- **Infrastructure:** Adaptadores, API REST, persistencia

**Ventajas:**
- Independencia de frameworks
- Facilita el testing
- Código más mantenible
- Bajo acoplamiento

### Frontend - Atomic Design

Atomic Design organiza los componentes en una jerarquía clara:

1. **Atoms:** Componentes básicos (Button, Input, Label)
2. **Molecules:** Combinación de átomos (FormField, SearchBar, Card)
3. **Organisms:** Componentes complejos (Header, Footer, UserForm)
4. **Templates:** Plantillas de páginas (MainTemplate)
5. **Pages:** Páginas con contenido real

**Ventajas:**
- Componentes altamente reutilizables
- Fácil de escalar
- Consistencia en el diseño
- Desarrollo más rápido

## 🛠️ Tecnologías

### Backend
- **Python 3.10+**
- **Poetry:** Gestión de dependencias
- **FastAPI:** Framework web moderno y rápido
- **Uvicorn:** Servidor ASGI
- **Pydantic:** Validación de datos

### Frontend
- **Next.js 14:** Framework React con App Router
- **TypeScript:** Tipado estático
- **Tailwind CSS:** Framework de CSS utility-first
- **React 18:** Biblioteca de UI

## 📝 Scripts Útiles

### Backend
```bash
# Instalar dependencias
poetry install

# Agregar nueva dependencia
poetry add <package>

# Ejecutar tests
poetry run pytest

# Formatear código
poetry run black .

# Linting
poetry run flake8
```

### Frontend
```bash
# Instalar dependencias
npm install

# Desarrollo
npm run dev

# Build
npm run build

# Producción
npm start

# Linting
npm run lint

# Type check
npm run type-check
```

## 🧪 Testing

### Backend
```bash
cd backend
poetry run pytest
```

### Frontend
```bash
cd frontend
npm test
```

## 📦 Deployment

### Backend
1. Configurar variables de entorno de producción
2. Build con Poetry: `poetry build`
3. Desplegar en el servidor de tu elección

### Frontend
1. Build: `npm run build`
2. Desplegar en Vercel, Netlify o tu servidor preferido

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.
