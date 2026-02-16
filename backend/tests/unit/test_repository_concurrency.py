"""
Tests de concurrencia para InMemoryUserRepository.

Verifica el comportamiento del repositorio bajo operaciones concurrentes.
"""

import asyncio

import pytest

from app.domain.entities.user import User
from app.infrastructure.persistence.in_memory_user_repository import \
    InMemoryUserRepository


@pytest.fixture
def repo() -> InMemoryUserRepository:
    """Crea una instancia limpia del repositorio en memoria."""
    return InMemoryUserRepository()


@pytest.mark.asyncio
async def test_concurrent_create_when_multiple_users_then_all_persisted(
    repo: InMemoryUserRepository,
) -> None:
    """Concurrencia: múltiples creaciones simultáneas persisten todos los usuarios."""
    # Arrange
    users = [User(phone=f"+5730012345{i:02d}") for i in range(10)]

    # Act
    results = await asyncio.gather(*[repo.create(user) for user in users])

    # Assert
    assert len(results) == 10
    all_users = await repo.find_all()
    assert len(all_users) == 10
    ids = [user.id for user in results]
    assert len(set(ids)) == 10


@pytest.mark.asyncio
async def test_concurrent_create_when_same_email_then_both_created(
    repo: InMemoryUserRepository,
) -> None:
    """Concurrencia: dos registros simultáneos con mismo email crean ambos."""
    # Arrange
    user_a = User(phone="+573001234567")
    user_b = User(phone="+573001234567")

    # Act
    results = await asyncio.gather(repo.create(user_a), repo.create(user_b))

    # Assert
    assert len(results) == 2
    assert results[0].id != results[1].id


@pytest.mark.asyncio
async def test_concurrent_read_write_when_creating_and_reading_then_no_error(
    repo: InMemoryUserRepository,
) -> None:
    """Concurrencia: lectura y escritura simultáneas no lanzan error."""
    # Arrange
    user = User(phone="+573001234567")
    created = await repo.create(user)

    # Act
    async def read_task() -> None:
        await repo.find_by_id(created.id or "")

    async def write_task() -> None:
        new_user = User(phone="+573001234568")
        await repo.create(new_user)

    await asyncio.gather(read_task(), write_task(), read_task(), write_task())

    # Assert
    all_users = await repo.find_all()
    assert len(all_users) == 3


@pytest.mark.asyncio
async def test_concurrent_delete_when_same_user_then_one_succeeds(
    repo: InMemoryUserRepository,
) -> None:
    """Concurrencia: eliminar el mismo usuario concurrentemente, al menos uno falla."""
    # Arrange
    user = User(phone="+573001234567")
    created = await repo.create(user)
    user_id = created.id or ""

    # Act
    results = await asyncio.gather(
        repo.delete(user_id),
        repo.delete(user_id),
    )

    # Assert
    assert True in results
    assert results.count(True) + results.count(False) == 2


@pytest.mark.asyncio
async def test_concurrent_update_when_same_user_then_last_write_wins(
    repo: InMemoryUserRepository,
) -> None:
    """Concurrencia: actualizaciones simultáneas del mismo usuario, última escritura gana."""
    # Arrange
    user = User(phone="+573001234567", email="original@example.com")
    created = await repo.create(user)

    # Act
    async def update_email(email: str) -> User:
        created.email = email
        return await repo.update(created)

    await asyncio.gather(
        update_email("update_a@example.com"),
        update_email("update_b@example.com"),
    )

    # Assert
    found = await repo.find_by_id(created.id or "")
    assert found is not None
    assert found.email in ("update_a@example.com", "update_b@example.com")
