"""
Tests unitarios para el router de health check.

Cubre casos positivos, negativos y edge cases del endpoint GET /health.
"""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_when_mongo_connected_then_returns_ok(
    client: AsyncClient,
) -> None:
    """Caso positivo: MongoDB conectado retorna status ok y mongodb connected."""
    # Arrange
    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        new_callable=AsyncMock,
        return_value=True,
    ):
        # Act
        response = await client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mongodb"] == "connected"
    assert data["app_name"] == "Backend Hexagonal"
    assert data["app_version"] == "0.1.0"


@pytest.mark.asyncio
async def test_health_check_when_mongo_disconnected_then_returns_disconnected(
    client: AsyncClient,
) -> None:
    """Caso negativo: MongoDB no conectado retorna mongodb disconnected."""
    # Arrange
    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        new_callable=AsyncMock,
        return_value=False,
    ):
        # Act
        response = await client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["mongodb"] == "disconnected"


@pytest.mark.asyncio
async def test_health_check_response_contains_all_fields(
    client: AsyncClient,
) -> None:
    """Edge case: La respuesta contiene todos los campos requeridos."""
    # Arrange
    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        new_callable=AsyncMock,
        return_value=True,
    ):
        # Act
        response = await client.get("/health")

    # Assert
    data = response.json()
    expected_keys = {"status", "app_name", "app_version", "mongodb"}
    assert set(data.keys()) == expected_keys


@pytest.mark.asyncio
async def test_health_check_when_ping_raises_exception_then_returns_disconnected(
    client: AsyncClient,
) -> None:
    """Caso negativo: Si ping_mongo lanza excepción, retorna disconnected."""
    # Arrange
    with patch(
        "app.adapters.inbound.http.routers.health_router.ping_mongo",
        new_callable=AsyncMock,
        side_effect=Exception("Connection error"),
    ):
        # Act & Assert
        with pytest.raises(Exception):
            await client.get("/health")
