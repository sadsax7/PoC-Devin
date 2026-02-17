"""
Configuración global de fixtures para PyTest.

Provee fixtures base para pruebas asíncronas y conexión
a MongoDB de test, alineado con BACKEND-GUIDELINES.md §5.3.

No incluye lógica de negocio — solo infraestructura de testing.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

# ============================================================
# Event Loop Fixture
# ============================================================


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Crea un event loop de sesión para todas las pruebas async.

    Scope 'session' evita recrear el loop por cada test,
    mejorando el rendimiento de la suite.

    Yields:
        asyncio.AbstractEventLoop: Event loop compartido.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ============================================================
# MongoDB Test Fixtures
# ============================================================


@pytest_asyncio.fixture(scope="session")
async def mongo_client() -> AsyncGenerator[AsyncIOMotorClient, None]:  # type: ignore[type-arg]
    """Cliente Motor conectado a la instancia de MongoDB de tests.

    Usa el puerto 27018 (servicio mongodb-test en docker-compose.yml).
    Se crea una sola vez por sesión de tests.

    Yields:
        AsyncIOMotorClient: Cliente de MongoDB async.
    """
    client: AsyncIOMotorClient = AsyncIOMotorClient(  # type: ignore[type-arg]
        "mongodb://admin:admin@localhost:27018",
        serverSelectionTimeoutMS=5000,
    )
    try:
        await client.admin.command("ping")
        yield client
    finally:
        client.close()


@pytest_asyncio.fixture()
async def test_db(
    mongo_client: AsyncIOMotorClient,  # type: ignore[type-arg]
) -> AsyncGenerator[AsyncIOMotorDatabase, None]:  # type: ignore[type-arg]
    """Base de datos limpia para cada test.

    Crea una DB y la limpia tras cada test,
    garantizando aislamiento (BACKEND-GUIDELINES.md §5.4).

    Args:
        mongo_client: Cliente Motor de sesión.

    Yields:
        AsyncIOMotorDatabase: Base de datos de test limpia.
    """
    db_name = "billetera_db_test"
    db: AsyncIOMotorDatabase = mongo_client[db_name]  # type: ignore[type-arg]
    yield db
    collections = await db.list_collection_names()
    for collection_name in collections:
        await db.drop_collection(collection_name)


# ============================================================
# Mock Fixtures (para Unit Tests sin DB)
# ============================================================


@pytest.fixture
def mock_user_repository() -> MagicMock:
    """Mock del puerto UserRepository para unit tests de use cases.

    Returns:
        MagicMock: Mock con métodos async simulados.
    """
    mock = MagicMock()
    mock.save = AsyncMock()
    mock.find_by_id = AsyncMock(return_value=None)
    mock.find_by_phone = AsyncMock(return_value=None)
    return mock


@pytest.fixture
def mock_password_hasher() -> MagicMock:
    """Mock del puerto PasswordHasherPort para unit tests.

    Returns:
        MagicMock: Mock que simula hashing de contraseñas.
    """
    mock = MagicMock()
    mock.hash_password = MagicMock(return_value="$argon2id$v=19$mocked_hash")
    mock.verify_password = MagicMock(return_value=True)
    return mock


@pytest.fixture
def mock_kyc_verification() -> MagicMock:
    """Mock del puerto KycVerificationPort para unit tests.

    Returns:
        MagicMock: Mock que simula verificación KYC aprobada.
    """
    mock = MagicMock()
    mock.verify = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_token_provider() -> MagicMock:
    """Mock del puerto TokenProviderPort para unit tests.

    Returns:
        MagicMock: Mock que simula generación de JWT tokens.
    """
    mock = MagicMock()
    mock.generate_access_token = MagicMock(return_value="mocked.access.token")
    mock.generate_refresh_token = MagicMock(return_value="mocked.refresh.token")
    mock.generate_mfa_token = MagicMock(return_value="mocked.mfa.token")
    mock.verify_token = MagicMock(return_value={"sub": "test_user_id", "type": "access"})
    return mock


@pytest.fixture
def mock_event_publisher() -> MagicMock:
    """Mock del puerto EventPublisherPort para unit tests.

    Returns:
        MagicMock: Mock que simula publicación de eventos de dominio.
    """
    mock = MagicMock()
    mock.publish = AsyncMock()
    return mock
