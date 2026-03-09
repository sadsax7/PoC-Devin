"""
Tests unitarios para GetUserProfileUseCase.

Cubre casos positivos, negativos, edge cases y validación
de sanitización (no se expone password_hash).
Referencia: HU-BE-03 AC#2-3, agents.md §5.1.7.

Patrón: AAA (Arrange-Act-Assert).
Nomenclatura: test_<unit>_when_<condition>_then_<expected>.
"""

from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.use_cases.get_user_profile import (
    GetUserProfileUseCase,
    UserProfileNotFoundError,
)
from app.domain.entities.user import KycStatus, User

# ── Helpers ───────────────────────────────────────────────────


def _make_user(
    *,
    user_id: str = "507f1f77bcf86cd799439011",
    phone: str = "+573001234567",
    email: str | None = "alice@example.com",
    name: str | None = "Alice",
    password_hash: str = "$argon2id$secret_hash",
    kyc_status: KycStatus = KycStatus.PENDING,
    mfa_enabled: bool = False,
    created_at: datetime | None = None,
) -> User:
    """Construye un User de dominio para tests."""
    if created_at is None:
        created_at = datetime(2026, 1, 30, 14, 23, 45, 123000, tzinfo=timezone.utc)
    return User(
        id=user_id,
        phone=phone,
        password_hash=password_hash,
        kyc_status=kyc_status,
        email=email,
        name=name,
        mfa_enabled=mfa_enabled,
        created_at=created_at,
    )


def _build_use_case(
    *,
    find_by_id_return: User | None = None,
) -> GetUserProfileUseCase:
    """Construye el caso de uso con mocks."""
    repo = MagicMock()
    repo.find_by_id = AsyncMock(return_value=find_by_id_return)
    return GetUserProfileUseCase(user_repository=repo)


# ── Casos positivos ───────────────────────────────────────────


class TestGetUserProfileSuccess:
    """Tests happy-path del caso de uso GetUserProfile."""

    @pytest.mark.asyncio
    async def test_execute_when_valid_user_id_then_returns_dto(self) -> None:
        """Usuario encontrado → retorna DTO con datos correctos."""
        # Arrange
        user = _make_user()
        uc = _build_use_case(find_by_id_return=user)

        # Act
        result = await uc.execute("507f1f77bcf86cd799439011")

        # Assert
        assert result.user_id == "507f1f77bcf86cd799439011"
        assert result.phone == "+573001234567"
        assert result.email == "alice@example.com"
        assert result.name == "Alice"
        assert result.kyc_status == "pending"
        assert result.mfa_enabled is False

    @pytest.mark.asyncio
    async def test_execute_when_user_approved_kyc_then_kyc_status_is_approved(
        self,
    ) -> None:
        """KYC APPROVED se mapea correctamente al string 'approved'."""
        # Arrange
        user = _make_user(kyc_status=KycStatus.APPROVED)
        uc = _build_use_case(find_by_id_return=user)

        # Act
        result = await uc.execute("507f1f77bcf86cd799439011")

        # Assert
        assert result.kyc_status == "approved"

    @pytest.mark.asyncio
    async def test_execute_when_mfa_enabled_then_mfa_returned_true(self) -> None:
        """mfa_enabled=True se propaga correctamente al DTO."""
        # Arrange
        user = _make_user(mfa_enabled=True)
        uc = _build_use_case(find_by_id_return=user)

        # Act
        result = await uc.execute("507f1f77bcf86cd799439011")

        # Assert
        assert result.mfa_enabled is True

    @pytest.mark.asyncio
    async def test_execute_when_valid_user_then_created_at_has_z_suffix(
        self,
    ) -> None:
        """created_at se retorna con sufijo 'Z' en ISO 8601."""
        # Arrange
        user = _make_user(created_at=datetime(2026, 1, 30, 14, 23, 45, 0, tzinfo=timezone.utc))
        uc = _build_use_case(find_by_id_return=user)

        # Act
        result = await uc.execute("507f1f77bcf86cd799439011")

        # Assert
        assert result.created_at.endswith("Z")

    @pytest.mark.asyncio
    async def test_execute_when_valid_user_then_password_hash_not_in_dto(
        self,
    ) -> None:
        """password_hash NUNCA se expone en el DTO (seguridad AC#3)."""
        # Arrange
        user = _make_user(password_hash="$argon2id$super_secret")
        uc = _build_use_case(find_by_id_return=user)

        # Act
        result = await uc.execute("507f1f77bcf86cd799439011")

        # Assert — verificar que el dataclass no expone el hash
        result_dict = dataclasses.asdict(result)
        assert "password_hash" not in result_dict


# ── Casos negativos ───────────────────────────────────────────


class TestGetUserProfileErrors:
    """Tests de error del caso de uso GetUserProfile."""

    @pytest.mark.asyncio
    async def test_execute_when_user_not_found_then_raises_not_found(
        self,
    ) -> None:
        """Usuario no encontrado → lanza UserProfileNotFoundError."""
        # Arrange
        uc = _build_use_case(find_by_id_return=None)

        # Act & Assert
        with pytest.raises(UserProfileNotFoundError):
            await uc.execute("nonexistent_id")

    @pytest.mark.asyncio
    async def test_execute_when_user_not_found_then_error_contains_user_id(
        self,
    ) -> None:
        """El mensaje de UserProfileNotFoundError incluye el user_id."""
        # Arrange
        uc = _build_use_case(find_by_id_return=None)

        # Act & Assert
        with pytest.raises(UserProfileNotFoundError, match="deleted_user_id"):
            await uc.execute("deleted_user_id")


# ── Edge cases ────────────────────────────────────────────────


class TestGetUserProfileEdgeCases:
    """Tests de edge cases del caso de uso GetUserProfile."""

    @pytest.mark.asyncio
    async def test_execute_when_email_is_none_then_email_none_in_dto(
        self,
    ) -> None:
        """Usuario sin email → campo email es None en el DTO."""
        # Arrange
        user = _make_user(email=None)
        uc = _build_use_case(find_by_id_return=user)

        # Act
        result = await uc.execute("507f1f77bcf86cd799439011")

        # Assert
        assert result.email is None

    @pytest.mark.asyncio
    async def test_execute_when_name_is_none_then_name_none_in_dto(self) -> None:
        """Usuario sin nombre → campo name es None en el DTO."""
        # Arrange
        user = _make_user(name=None)
        uc = _build_use_case(find_by_id_return=user)

        # Act
        result = await uc.execute("507f1f77bcf86cd799439011")

        # Assert
        assert result.name is None

    @pytest.mark.asyncio
    async def test_execute_when_kyc_rejected_then_kyc_status_is_rejected(
        self,
    ) -> None:
        """KYC REJECTED se mapea al string 'rejected'."""
        # Arrange
        user = _make_user(kyc_status=KycStatus.REJECTED)
        uc = _build_use_case(find_by_id_return=user)

        # Act
        result = await uc.execute("507f1f77bcf86cd799439011")

        # Assert
        assert result.kyc_status == "rejected"

    @pytest.mark.asyncio
    async def test_execute_when_created_at_has_microseconds_then_iso_format_correct(
        self,
    ) -> None:
        """created_at con microsegundos se serializa correctamente."""
        # Arrange
        created = datetime(2026, 1, 30, 14, 23, 45, 123456, tzinfo=timezone.utc)
        user = _make_user(created_at=created)
        uc = _build_use_case(find_by_id_return=user)

        # Act
        result = await uc.execute("507f1f77bcf86cd799439011")

        # Assert
        assert "123456" in result.created_at
        assert result.created_at.endswith("Z")

    @pytest.mark.asyncio
    async def test_execute_calls_repository_with_correct_user_id(self) -> None:
        """El caso de uso llama al repositorio con el user_id recibido."""
        # Arrange
        user = _make_user()
        repo = MagicMock()
        repo.find_by_id = AsyncMock(return_value=user)
        uc = GetUserProfileUseCase(user_repository=repo)
        specific_id = "abc123xyz"

        # Act
        await uc.execute(specific_id)

        # Assert
        repo.find_by_id.assert_awaited_once_with(specific_id)
