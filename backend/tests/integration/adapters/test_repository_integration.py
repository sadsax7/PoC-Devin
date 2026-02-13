"""
Tests de integración para InMemoryUserRepository.

Verifica el flujo completo de operaciones CRUD del repositorio,
incluyendo escenarios de error y transiciones de estado.
"""

import pytest

from app.domain.entities.user import User
from app.infrastructure.persistence.in_memory_user_repository import \
    InMemoryUserRepository


@pytest.fixture
def repo() -> InMemoryUserRepository:
    """Crea una instancia limpia del repositorio en memoria."""
    return InMemoryUserRepository()


@pytest.mark.asyncio
async def test_full_crud_lifecycle(repo: InMemoryUserRepository) -> None:
    """Integración: ciclo CRUD completo create → read → update → delete."""
    # Arrange & Act - Create
    user = User(email="lifecycle@example.com", password_hash="hash123")
    created = await repo.create(user)
    assert created.id is not None

    # Act - Read
    found = await repo.find_by_id(created.id or "")
    assert found is not None
    assert found.email == "lifecycle@example.com"

    # Act - Update
    found.email = "updated@example.com"
    updated = await repo.update(found)
    assert updated.email == "updated@example.com"

    # Act - Delete
    deleted = await repo.delete(created.id or "")
    assert deleted is True

    # Assert - Verify deletion
    after_delete = await repo.find_by_id(created.id or "")
    assert after_delete is None


@pytest.mark.asyncio
async def test_find_by_email_after_update_when_email_changed_then_found_by_new(
    repo: InMemoryUserRepository,
) -> None:
    """Integración: después de actualizar email, se encuentra por el nuevo."""
    # Arrange
    user = User(email="old@example.com")
    created = await repo.create(user)

    # Act
    created.email = "new@example.com"
    await repo.update(created)

    # Assert
    found_old = await repo.find_by_email("old@example.com")
    found_new = await repo.find_by_email("new@example.com")
    assert found_old is None
    assert found_new is not None
    assert found_new.email == "new@example.com"


@pytest.mark.asyncio
async def test_create_multiple_then_find_all_returns_correct_count(
    repo: InMemoryUserRepository,
) -> None:
    """Integración: crear múltiples usuarios y verificar find_all."""
    # Arrange & Act
    for i in range(5):
        await repo.create(User(email=f"user{i}@example.com"))

    # Assert
    all_users = await repo.find_all()
    assert len(all_users) == 5


@pytest.mark.asyncio
async def test_delete_then_create_with_same_email_then_new_id(
    repo: InMemoryUserRepository,
) -> None:
    """Integración: eliminar y recrear con mismo email genera nuevo ID."""
    # Arrange
    user = User(email="recycle@example.com")
    created = await repo.create(user)
    old_id = created.id

    # Act
    await repo.delete(old_id or "")
    new_user = User(email="recycle@example.com")
    recreated = await repo.create(new_user)

    # Assert
    assert recreated.id != old_id
    assert recreated.email == "recycle@example.com"


@pytest.mark.asyncio
async def test_update_nonexistent_after_delete_then_raises_error(
    repo: InMemoryUserRepository,
) -> None:
    """Integración: actualizar usuario eliminado lanza ValueError."""
    # Arrange
    user = User(email="ghost@example.com")
    created = await repo.create(user)
    await repo.delete(created.id or "")

    # Act & Assert
    with pytest.raises(ValueError, match="no encontrado"):
        await repo.update(created)
