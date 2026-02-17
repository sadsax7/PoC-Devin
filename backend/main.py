"""
Punto de entrada de la aplicación FastAPI.

Configura la aplicación, conecta a MongoDB y expone el endpoint
de health check según HU-BE-00 Acceptance Criteria #4.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona el ciclo de vida de la aplicación.

    Establece conexión a MongoDB al iniciar y la cierra al detener.

    Args:
        app: Instancia de FastAPI.

    Yields:
        None: Control al framework durante la vida de la app.
    """
    app.state.mongo_client = AsyncIOMotorClient(settings.mongodb_uri)
    app.state.db = app.state.mongo_client[settings.mongodb_db_name]

    await app.state.mongo_client.admin.command("ping")

    yield

    app.state.mongo_client.close()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


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
