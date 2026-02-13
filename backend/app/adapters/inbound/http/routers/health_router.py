"""
Router de health check para la API.

Provee el endpoint GET /health que verifica el estado del servicio
y la conectividad con MongoDB.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.adapters.outbound.db.mongo_client import ping_mongo
from app.config.settings import settings

router = APIRouter()


class HealthResponse(BaseModel):
    """Modelo de respuesta del endpoint de health check.

    Attributes:
        status: Estado general del servicio.
        app_name: Nombre de la aplicación.
        app_version: Versión de la aplicación.
        mongodb: Estado de la conexión con MongoDB.
    """

    status: str
    app_name: str
    app_version: str
    mongodb: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Verifica el estado del servicio y la conexión a MongoDB.

    Returns:
        HealthResponse con el estado del servicio y MongoDB.
    """
    mongo_ok = await ping_mongo()
    mongo_status = "connected" if mongo_ok else "disconnected"

    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        app_version=settings.app_version,
        mongodb=mongo_status,
    )
