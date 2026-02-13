"""
Tests unitarios para InMemoryUserRepository.

Cubre casos positivos, negativos y edge cases.
"""

import pytest

from app.domain.entities.user import User
from app.infrastructure.persistence import InMemoryUserRepository


@pytest.fixture
def repo() -> InMemoryUserRepository:
    """Crea una instancia limpia del repositorio en memoria."""
    return InMemoryUserRepository()


@pytest.mark.asyncio
async def test_create_when_valid_user_then_assigns_id(
    repo: InMemoryUserRepository,
) -> None:
    """Caso positivo: create asigna un id al usuario."""
    # Arrange
    user = User(email="test@example.com", password_hash="hashed")

    # Act
    result = await repo.create(user)

    # Assert
    assert result.id is not None
    assert result.email == "test@example.com"


@pytest.mark.asyncio
async def test_find_by_id_when_exists_then_returns_user(
    repo: InMemoryUserRepository,
) -> None:
    """Caso positivo: find_by_id retorna el usuario existente."""
    # Arrange
    user = User(email="test@example.com")
    created = await repo.create(user)

    # Act
    found = await repo.find_by_id(created.id or "")

    # Assert
    assert found is not None
    assert found.email == "test@example.com"


@pytest.mark.asyncio
async def test_find_by_id_when_not_exists_then_returns_none(
    repo: InMemoryUserRepository,
) -> None:
    """Caso negativo: find_by_id retorna None si no existe."""
    # Arrange & Act
    result = await repo.find_by_id("nonexistent")

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_find_by_email_when_exists_then_returns_user(
    repo: InMemoryUserRepository,
) -> None:
    """Caso positivo: find_by_email retorna el usuario existente."""
    # Arrange
    user = User(email="find@example.com")
    await repo.create(user)

    # Act
    found = await repo.find_by_email("find@example.com")

    # Assert
    assert found is not None
    assert found.email == "find@example.com"


@pytest.mark.asyncio
async def test_find_by_email_when_not_exists_then_returns_none(
    repo: InMemoryUserRepository,
) -> None:
    """Caso negativo: find_by_email retorna None si no existe."""
    # Arrange & Act
    result = await repo.find_by_email("nonexistent@example.com")

    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_find_all_when_empty_then_returns_empty_list(
    repo: InMemoryUserRepository,
) -> None:
    """Edge case: find_all retorna lista vacía si no hay usuarios."""
    # Arrange & Act
    result = await repo.find_all()

    # Assert
    assert result == []


@pytest.mark.asyncio
async def test_find_all_when_users_exist_then_returns_all(
    repo: InMemoryUserRepository,
) -> None:
    """Caso positivo: find_all retorna todos los usuarios."""
    # Arrange
    await repo.create(User(email="a@example.com"))
    await repo.create(User(email="b@example.com"))

    # Act
    result = await repo.find_all()

    # Assert
    assert len(result) == 2


@pytest.mark.asyncio
async def test_update_when_exists_then_updates_user(
    repo: InMemoryUserRepository,
) -> None:
    """Caso positivo: update modifica el usuario existente."""
    # Arrange
    user = User(email="old@example.com")
    created = await repo.create(user)
    created.email = "new@example.com"

    # Act
    updated = await repo.update(created)

    # Assert
    assert updated.email == "new@example.com"


@pytest.mark.asyncio
async def test_update_when_not_exists_then_raises_value_error(
    repo: InMemoryUserRepository,
) -> None:
    """Caso negativo: update lanza ValueError si no existe."""
    # Arrange
    user = User(email="ghost@example.com", id="nonexistent")

    # Act & Assert
    with pytest.raises(ValueError, match="no encontrado"):
        await repo.update(user)


@pytest.mark.asyncio
async def test_delete_when_exists_then_returns_true(
    repo: InMemoryUserRepository,
) -> None:
    """Caso positivo: delete retorna True si el usuario fue eliminado."""
    # Arrange
    user = User(email="delete@example.com")
    created = await repo.create(user)

    # Act
    result = await repo.delete(created.id or "")

    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_delete_when_not_exists_then_returns_false(
    repo: InMemoryUserRepository,
) -> None:
    """Caso negativo: delete retorna False si no existe."""
    # Arrange & Act
    result = await repo.delete("nonexistent")

    # Assert
    assert result is False
