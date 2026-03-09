"""
Punto de entrada de la aplicación FastAPI.

Configura la aplicación, conecta a MongoDB y expone el endpoint
de health check según HU-BE-00 Acceptance Criteria #4.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.adapters.inbound.http.routers.auth_router import router as auth_router
from app.adapters.outbound.db.user_repository_impl import UserRepositoryImpl
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona el ciclo de vida de la aplicación.

    Establece conexión a MongoDB al iniciar y la cierra al detener.
    Crea los índices necesarios (HU-BE-01 AC#1).

    Args:
        app: Instancia de FastAPI.

    Yields:
        None: Control al framework durante la vida de la app.
    """
    app.state.mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    app.state.db = app.state.mongo_client[settings.mongodb_db_name]

    await app.state.mongo_client.admin.command("ping")

    # Crear índices al inicio (HU-BE-01 AC#1)
    user_repo = UserRepositoryImpl(app.state.db)
    await user_repo.ensure_indexes()

    yield

    app.state.mongo_client.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.include_router(auth_router)


@app.get("/health", tags=["Infrastructure"])
async def health_check() -> dict[str, str]:
    """Health check endpoint.

    Verifica que la API esté activa y MongoDB responda.
    HU-BE-00 Acceptance Criteria #4.

    Returns:
        dict: Estado de la API y conexión a MongoDB.
    """
    try:
        await app.state.mongo_client.admin.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok",
        "database": db_status,
        "version": settings.app_version,
    }
