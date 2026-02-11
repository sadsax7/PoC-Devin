# Backend - Arquitectura Hexagonal

## Estructura

```
backend/
├── application/          # Capa de aplicación (casos de uso)
│   ├── use_cases/       # Casos de uso
│   └── ports/           # Interfaces (puertos)
├── domain/              # Capa de dominio
│   ├── entities/        # Entidades del negocio
│   ├── value_objects/   # Objetos de valor
│   └── repositories/    # Interfaces de repositorios
├── infrastructure/      # Capa de infraestructura
│   ├── api/            # API REST (FastAPI)
│   ├── persistence/    # Implementación de repositorios
│   └── config/         # Configuración
├── main.py             # Punto de entrada
└── pyproject.toml      # Configuración de Poetry
```

## Instalación

```bash
poetry install
```

## Ejecución

```bash
poetry run python main.py
```

## Tests

```bash
poetry run pytest
```
