# Backend - Arquitectura Hexagonal

## Estructura

```
backend/
├── app/
│   ├── domain/              # Lógica de negocio pura
│   │   ├── entities/        # Entidades con identidad
│   │   ├── value_objects/   # Objetos inmutables por valor
│   │   ├── services/        # Servicios de dominio
│   │   ├── ports/           # Interfaces (contratos)
│   │   └── repositories/    # Interfaces de repositorios
│   ├── application/         # Orquestación
│   │   ├── use_cases/       # Casos de uso
│   │   └── dtos/            # Data Transfer Objects
│   ├── adapters/            # Implementaciones
│   │   ├── inbound/http/    # Routers FastAPI
│   │   └── outbound/        # DB, KYC, Security, Messaging
│   ├── config/              # Configuración (Pydantic Settings)
│   └── shared/              # Utilidades transversales
├── tests/
│   ├── unit/                # Tests sin DB ni HTTP
│   │   ├── domain/
│   │   └── application/
│   └── integration/         # Tests con sistemas externos
│       └── adapters/
├── main.py                  # Punto de entrada FastAPI
└── pyproject.toml           # Configuración de Poetry
```

## Pre-requisitos

- Python 3.10+
- Poetry
- Docker & Docker Compose (para MongoDB)

## Instalación

```bash
# Levantar MongoDB
cd ..  # raíz del monorepo
docker compose up -d

# Instalar dependencias
cd backend
poetry install
```

## Ejecución

```bash
poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Health Check

```bash
curl http://localhost:8000/health
# {"status": "ok", "database": "connected", "version": "0.1.0"}
```

## Tests

```bash
poetry run pytest
```

## Quality Gates

```bash
# Formato
poetry run black app/ tests/
poetry run isort app/ tests/

# Linting
poetry run ruff check app/ tests/

# Typing
poetry run mypy app/

# Complejidad
poetry run radon cc app/ -a -nc

# Tests con cobertura
poetry run pytest --cov=app --cov-report=term-missing
```
