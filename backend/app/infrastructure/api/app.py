"""
Fábrica de la aplicación FastAPI.

Crea y configura la instancia de FastAPI, registra routers
y gestiona el ciclo de vida de conexiones externas.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.adapters.inbound.http.routers.health_router import \
    router as health_router
from app.adapters.outbound.db.mongo_client import (connect_mongo,
                                                   disconnect_mongo)
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Gestiona el ciclo de vida de la aplicación.

    Conecta a MongoDB al iniciar y desconecta al cerrar.

    Args:
        app: Instancia de FastAPI.

    Yields:
        None después de establecer la conexión.
    """
    await connect_mongo(settings.mongodb_uri, settings.mongodb_database)
    yield
    await disconnect_mongo()


def create_app() -> FastAPI:
    """Crea y configura la instancia de FastAPI.

    Returns:
        Instancia de FastAPI configurada con routers y lifespan.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.include_router(health_router)

    return app
