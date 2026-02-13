"""
Tests unitarios para el cliente MongoDB asíncrono.

Cubre casos positivos, negativos y edge cases de connect, disconnect,
get_database y ping_mongo.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.adapters.outbound.db import mongo_client


@pytest.fixture(autouse=True)
def reset_mongo_state() -> None:
    """Resetea el estado global del módulo mongo_client antes de cada test."""
    mongo_client._client = None
    mongo_client._database = None


@pytest.mark.asyncio
async def test_connect_mongo_when_valid_uri_then_client_created() -> None:
    """Caso positivo: connect_mongo crea un cliente y asigna la base de datos."""
    # Arrange
    mock_client_instance = MagicMock()
    mock_db = MagicMock()
    mock_client_instance.__getitem__ = MagicMock(return_value=mock_db)

    with patch(
        "app.adapters.outbound.db.mongo_client.AsyncIOMotorClient",
        return_value=mock_client_instance,
    ):
        # Act
        await mongo_client.connect_mongo("mongodb://localhost:27017", "test_db")

    # Assert
    assert mongo_client._client is not None
    assert mongo_client._database is not None


@pytest.mark.asyncio
async def test_disconnect_mongo_when_connected_then_client_closed() -> None:
    """Caso positivo: disconnect_mongo cierra el cliente y limpia el estado."""
    # Arrange
    mock_client = MagicMock()
    mongo_client._client = mock_client
    mongo_client._database = MagicMock()

    # Act
    await mongo_client.disconnect_mongo()

    # Assert
    mock_client.close.assert_called_once()
    assert mongo_client._client is None
    assert mongo_client._database is None


@pytest.mark.asyncio
async def test_disconnect_mongo_when_not_connected_then_no_error() -> None:
    """Edge case: disconnect_mongo cuando no hay conexión no lanza error."""
    # Arrange (estado ya es None por el fixture)

    # Act
    await mongo_client.disconnect_mongo()

    # Assert
    assert mongo_client._client is None
    assert mongo_client._database is None


def test_get_database_when_connected_then_returns_database() -> None:
    """Caso positivo: get_database retorna la base de datos configurada."""
    # Arrange
    mock_db = MagicMock()
    mongo_client._database = mock_db

    # Act
    result = mongo_client.get_database()

    # Assert
    assert result is mock_db


def test_get_database_when_not_connected_then_raises_runtime_error() -> None:
    """Caso negativo: get_database sin conexión lanza RuntimeError."""
    # Arrange (estado ya es None por el fixture)

    # Act & Assert
    with pytest.raises(RuntimeError, match="MongoDB no está conectado"):
        mongo_client.get_database()


@pytest.mark.asyncio
async def test_ping_mongo_when_connected_and_ok_then_returns_true() -> None:
    """Caso positivo: ping exitoso retorna True."""
    # Arrange
    mock_client = MagicMock()
    mock_admin = MagicMock()
    mock_admin.command = AsyncMock(return_value={"ok": 1.0})
    mock_client.admin = mock_admin
    mongo_client._client = mock_client

    # Act
    result = await mongo_client.ping_mongo()

    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_ping_mongo_when_not_connected_then_returns_false() -> None:
    """Caso negativo: sin cliente conectado retorna False."""
    # Arrange (estado ya es None por el fixture)

    # Act
    result = await mongo_client.ping_mongo()

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_ping_mongo_when_command_fails_then_returns_false() -> None:
    """Caso negativo: si el comando ping falla retorna False."""
    # Arrange
    mock_client = MagicMock()
    mock_admin = MagicMock()
    mock_admin.command = AsyncMock(side_effect=Exception("Connection refused"))
    mock_client.admin = mock_admin
    mongo_client._client = mock_client

    # Act
    result = await mongo_client.ping_mongo()

    # Assert
    assert result is False


@pytest.mark.asyncio
async def test_ping_mongo_when_ok_not_one_then_returns_false() -> None:
    """Edge case: si el resultado del ping no tiene ok=1.0 retorna False."""
    # Arrange
    mock_client = MagicMock()
    mock_admin = MagicMock()
    mock_admin.command = AsyncMock(return_value={"ok": 0.0})
    mock_client.admin = mock_admin
    mongo_client._client = mock_client

    # Act
    result = await mongo_client.ping_mongo()

    # Assert
    assert result is False
