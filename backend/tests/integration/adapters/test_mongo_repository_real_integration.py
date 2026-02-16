"""Tests de integracion real con MongoDB para MongoUserRepository.

Estos tests requieren una instancia de MongoDB corriendo en localhost:27017.
Verifican persistencia real, indices unicos y transiciones de estado KYC.
Marcados con @pytest.mark.integration.
"""

from datetime import datetime, timezone
from typing import AsyncIterator

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient

from app.adapters.outbound.db.user_repository_impl import MongoUserRepository
from app.domain.entities.user import User

TEST_DB_NAME = "billetera_virtual_test"
MONGO_URI = "mongodb://localhost:27017"


@pytest_asyncio.fixture
async def mongo_repo() -> AsyncIterator[MongoUserRepository]:
    """Crea un repositorio MongoDB real con base de datos de test.

    Yields:
        MongoUserRepository conectado a la base de datos de test.
    """
    client: AsyncIOMotorClient = AsyncIOMotorClient(MONGO_URI)  # type: ignore[type-arg]
    database = client[TEST_DB_NAME]
    repo = MongoUserRepository(database)
    await repo.ensure_indexes()
    yield repo
    await database.drop_collection(MongoUserRepository.COLLECTION_NAME)
    client.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_create_and_find_by_phone_when_valid_then_persists(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: crear usuario y recuperarlo por telefono persiste en MongoDB."""
    # Arrange
    user = User(
        phone="+573001234567",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$test_hash",
        email="test@example.com",
        name="Test User",
        kyc_status="pending",
        mfa_enabled=False,
    )

    # Act
    created = await mongo_repo.create(user)
    found = await mongo_repo.find_by_phone("+573001234567")

    # Assert
    assert created.id is not None
    assert found is not None
    assert found.phone == "+573001234567"
    assert found.email == "test@example.com"
    assert found.name == "Test User"
    assert found.password_hash == "$argon2id$v=19$m=65536,t=3,p=4$test_hash"
    assert found.kyc_status == "pending"
    assert found.mfa_enabled is False
    assert isinstance(found.created_at, datetime)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_create_duplicate_phone_then_raises_error(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: telefono duplicado lanza error por indice unico."""
    # Arrange
    user1 = User(
        phone="+573001234567",
        password_hash="hash1",
        kyc_status="pending",
    )
    user2 = User(
        phone="+573001234567",
        password_hash="hash2",
        kyc_status="pending",
    )

    # Act
    await mongo_repo.create(user1)

    # Assert
    with pytest.raises(Exception):
        await mongo_repo.create(user2)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_kyc_status_transitions_persist_correctly(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: transiciones de estado KYC se persisten correctamente."""
    # Arrange - Create users with different KYC statuses
    pending_user = User(
        phone="+573001234501",
        password_hash="hash_pending",
        kyc_status="pending",
    )
    approved_user = User(
        phone="+573001234599",
        password_hash="hash_approved",
        kyc_status="approved",
    )

    # Act
    await mongo_repo.create(pending_user)
    await mongo_repo.create(approved_user)
    found_pending = await mongo_repo.find_by_phone("+573001234501")
    found_approved = await mongo_repo.find_by_phone("+573001234599")

    # Assert
    assert found_pending is not None
    assert found_pending.kyc_status == "pending"
    assert found_approved is not None
    assert found_approved.kyc_status == "approved"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_find_by_phone_when_not_exists_then_returns_none(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: buscar telefono inexistente retorna None."""
    # Act
    result = await mongo_repo.find_by_phone("+573009999999")

    # Assert
    assert result is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_find_by_email_when_exists_then_returns_user(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: buscar por email existente retorna usuario."""
    # Arrange
    user = User(
        phone="+573001234567",
        password_hash="hash",
        email="findme@example.com",
        kyc_status="pending",
    )
    await mongo_repo.create(user)

    # Act
    found = await mongo_repo.find_by_email("findme@example.com")

    # Assert
    assert found is not None
    assert found.email == "findme@example.com"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_find_by_id_when_exists_then_returns_user(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: buscar por ID existente retorna usuario."""
    # Arrange
    user = User(
        phone="+573001234567",
        password_hash="hash",
        kyc_status="pending",
    )
    created = await mongo_repo.create(user)
    assert created.id is not None

    # Act
    found = await mongo_repo.find_by_id(created.id)

    # Assert
    assert found is not None
    assert found.id == created.id
    assert found.phone == "+573001234567"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_find_all_when_multiple_users_then_returns_all(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: find_all retorna todos los usuarios."""
    # Arrange
    await mongo_repo.create(User(phone="+573001234501", password_hash="h1", kyc_status="pending"))
    await mongo_repo.create(User(phone="+573001234502", password_hash="h2", kyc_status="approved"))

    # Act
    users = await mongo_repo.find_all()

    # Assert
    assert len(users) == 2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_update_when_exists_then_persists_changes(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: actualizar usuario persiste los cambios."""
    # Arrange
    user = User(
        phone="+573001234567",
        password_hash="hash",
        email="old@example.com",
        kyc_status="pending",
    )
    created = await mongo_repo.create(user)
    created.email = "new@example.com"
    created.kyc_status = "approved"

    # Act
    await mongo_repo.update(created)
    found = await mongo_repo.find_by_phone("+573001234567")

    # Assert
    assert found is not None
    assert found.email == "new@example.com"
    assert found.kyc_status == "approved"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_delete_when_exists_then_removes_user(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: eliminar usuario lo remueve de la coleccion."""
    # Arrange
    user = User(
        phone="+573001234567",
        password_hash="hash",
        kyc_status="pending",
    )
    created = await mongo_repo.create(user)
    assert created.id is not None

    # Act
    deleted = await mongo_repo.delete(created.id)
    found = await mongo_repo.find_by_phone("+573001234567")

    # Assert
    assert deleted is True
    assert found is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_delete_when_not_exists_then_returns_false(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: eliminar usuario inexistente retorna False."""
    # Act
    result = await mongo_repo.delete("507f1f77bcf86cd799439011")

    # Assert
    assert result is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_mongo_created_at_preserves_timezone(
    mongo_repo: MongoUserRepository,
) -> None:
    """Integracion: created_at preserva la zona horaria UTC."""
    # Arrange
    now = datetime.now(timezone.utc)
    user = User(
        phone="+573001234567",
        password_hash="hash",
        kyc_status="pending",
        created_at=now,
    )

    # Act
    await mongo_repo.create(user)
    found = await mongo_repo.find_by_phone("+573001234567")

    # Assert
    assert found is not None
    assert found.created_at.tzinfo is not None
