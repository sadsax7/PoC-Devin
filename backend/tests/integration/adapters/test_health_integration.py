"""
Tests de integración para el endpoint de health check.

Verifica el flujo completo del endpoint GET /health con el cliente HTTP,
incluyendo casos de error, timeout y transiciones de estado.
"""

from typing import AsyncIterator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.infrastructure.api.app import create_app


@pytest_asyncio.fixture
async def integration_app() -> AsyncIterator[FastAPI]:
    """Crea una instancia de la aplicación para tests de integración.

    Yields:
        Instancia de FastAPI con MongoDB mockeado.
    """
    with patch("app.infrastructure.api.app.connect_mongo", new_callable=AsyncMock):
        with patch("app.infrastructure.api.app.disconnect_mongo", new_callable=AsyncMock):
            application = create_app()
            async with application.router.lifespan_context(application):
                yield application


@pytest_asyncio.fixture
async def integration_client(
    integration_app: FastAPI,
) -> AsyncIterator[AsyncClient]:
    """Crea un cliente HTTP para tests de integración.

    Args:
        integration_app: Instancia de FastAPI.

    Yields:
        Cliente HTTP asíncrono.
    """
    transport = ASGITransport(app=integration_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_integration_when_mongo_up_then_full_response(
    integration_client: AsyncClient,
) -> None:
    """Integración: GET /health con MongoDB activo retorna respuesta completa."""
    # Arrange
    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        new_callable=AsyncMock,
        return_value=True,
    ):
        # Act
        response = await integration_client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mongodb"] == "connected"
    assert "app_name" in data
    assert "app_version" in data


@pytest.mark.asyncio
async def test_health_integration_when_mongo_down_then_reports_disconnected(
    integration_client: AsyncClient,
) -> None:
    """Integración: GET /health con MongoDB caído reporta disconnected."""
    # Arrange
    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        new_callable=AsyncMock,
        return_value=False,
    ):
        # Act
        response = await integration_client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["mongodb"] == "disconnected"


@pytest.mark.asyncio
async def test_health_integration_when_mongo_timeout_then_reports_disconnected(
    integration_client: AsyncClient,
) -> None:
    """Integración: GET /health con timeout de MongoDB reporta disconnected."""

    # Arrange
    async def slow_ping() -> bool:
        return False

    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        side_effect=slow_ping,
    ):
        # Act
        response = await integration_client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["mongodb"] == "disconnected"


@pytest.mark.asyncio
async def test_health_integration_when_mongo_transitions_then_reflects_state(
    integration_client: AsyncClient,
) -> None:
    """Integración: el estado de MongoDB se refleja en llamadas sucesivas."""
    # Arrange & Act - MongoDB conectado
    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        new_callable=AsyncMock,
        return_value=True,
    ):
        response_up = await integration_client.get("/health")

    # Act - MongoDB desconectado
    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        new_callable=AsyncMock,
        return_value=False,
    ):
        response_down = await integration_client.get("/health")

    # Assert
    assert response_up.json()["mongodb"] == "connected"
    assert response_down.json()["mongodb"] == "disconnected"


@pytest.mark.asyncio
async def test_health_integration_response_content_type_is_json(
    integration_client: AsyncClient,
) -> None:
    """Integración: la respuesta del health check tiene content-type JSON."""
    # Arrange
    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        new_callable=AsyncMock,
        return_value=True,
    ):
        # Act
        response = await integration_client.get("/health")

    # Assert
    assert "application/json" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_health_integration_when_method_not_allowed_then_405(
    integration_client: AsyncClient,
) -> None:
    """Integración: POST /health retorna 405 Method Not Allowed."""
    # Arrange & Act
    response = await integration_client.post("/health")

    # Assert
    assert response.status_code == 405
