"""
Tests de integración para UserRepositoryImpl (MongoDB real).

Usa la instancia de test en el puerto 27018.
Referencia: HU-BE-01 DoD#11, BACKEND-GUIDELINES.md §5.4
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.adapters.outbound.db.user_repository_impl import UserRepositoryImpl
from app.domain.entities.user import KycStatus, User

# All tests in this module share the session event-loop (Motor client is session-scoped).
pytestmark = pytest.mark.asyncio(loop_scope="session")


@pytest_asyncio.fixture(loop_scope="session")
async def user_repo(
    test_db: AsyncIOMotorDatabase,
) -> UserRepositoryImpl:
    """Provee un UserRepositoryImpl conectado a la DB de test.

    Args:
        test_db: Base de datos de test limpiada por conftest.

    Returns:
        UserRepositoryImpl listo para usar.
    """
    repo = UserRepositoryImpl(test_db)
    await repo.ensure_indexes()
    return repo


# ============================================================
# Positivos
# ============================================================


class TestUserRepositoryImplSave:
    """Tests de persistencia exitosa."""

    async def test_save_when_valid_user_then_returns_id(
        self, user_repo: UserRepositoryImpl
    ) -> None:
        """save() retorna un ID string no vacío."""
        user = User(
            phone="+573001234567",
            password_hash="$argon2id$hash",
            kyc_status=KycStatus.PENDING,
        )
        user_id = await user_repo.save(user)
        assert isinstance(user_id, str)
        assert len(user_id) > 0

    async def test_save_when_user_with_email_then_persisted(
        self, user_repo: UserRepositoryImpl
    ) -> None:
        """Usuario con email se persiste correctamente."""
        user = User(
            phone="+573001234568",
            password_hash="$argon2id$hash",
            kyc_status=KycStatus.APPROVED,
            email="test@example.com",
            name="Test User",
        )
        user_id = await user_repo.save(user)
        found = await user_repo.find_by_id(user_id)
        assert found is not None
        assert found.email == "test@example.com"
        assert found.name == "Test User"


# ============================================================
# find_by_phone
# ============================================================


class TestUserRepositoryImplFindByPhone:
    """Tests de búsqueda por teléfono."""

    async def test_find_by_phone_when_exists_then_returns_user(
        self, user_repo: UserRepositoryImpl
    ) -> None:
        """Encuentra usuario existente por teléfono."""
        user = User(
            phone="+573001234567",
            password_hash="$argon2id$hash",
            kyc_status=KycStatus.PENDING,
        )
        await user_repo.save(user)
        found = await user_repo.find_by_phone("+573001234567")
        assert found is not None
        assert found.phone == "+573001234567"

    async def test_find_by_phone_when_not_exists_then_returns_none(
        self, user_repo: UserRepositoryImpl
    ) -> None:
        """Retorna None si el teléfono no existe."""
        found = await user_repo.find_by_phone("+573009999999")
        assert found is None


# ============================================================
# find_by_id
# ============================================================


class TestUserRepositoryImplFindById:
    """Tests de búsqueda por ID."""

    async def test_find_by_id_when_exists_then_returns_user(
        self, user_repo: UserRepositoryImpl
    ) -> None:
        """Encuentra usuario por ID generado."""
        user = User(
            phone="+573001234567",
            password_hash="$argon2id$hash",
            kyc_status=KycStatus.APPROVED,
        )
        user_id = await user_repo.save(user)
        found = await user_repo.find_by_id(user_id)
        assert found is not None
        assert found.id == user_id

    async def test_find_by_id_when_not_exists_then_returns_none(
        self, user_repo: UserRepositoryImpl
    ) -> None:
        """Retorna None si el ID no existe."""
        found = await user_repo.find_by_id("000000000000000000000000")
        assert found is None


# ============================================================
# ensure_indexes (unique phone constraint)
# ============================================================


class TestUserRepositoryImplIndexes:
    """Tests de índices."""

    async def test_ensure_indexes_when_duplicate_phone_then_raises(
        self, user_repo: UserRepositoryImpl
    ) -> None:
        """Índice único impide teléfonos duplicados."""
        user1 = User(
            phone="+573001234567",
            password_hash="$argon2id$hash1",
            kyc_status=KycStatus.PENDING,
        )
        await user_repo.save(user1)

        user2 = User(
            phone="+573001234567",
            password_hash="$argon2id$hash2",
            kyc_status=KycStatus.PENDING,
        )
        with pytest.raises(Exception, match="duplicate key"):  # DuplicateKeyError
            await user_repo.save(user2)


# ============================================================
# Edge cases
# ============================================================


class TestUserRepositoryImplEdgeCases:
    """Edge cases de persistencia."""

    async def test_save_when_minimal_user_then_optional_fields_none(
        self, user_repo: UserRepositoryImpl
    ) -> None:
        """Usuario mínimo: email y name son None al recuperar."""
        user = User(
            phone="+573001234567",
            password_hash="$argon2id$hash",
            kyc_status=KycStatus.PENDING,
        )
        user_id = await user_repo.save(user)
        found = await user_repo.find_by_id(user_id)
        assert found is not None
        assert found.email is None
        assert found.name is None
        assert found.mfa_enabled is False
