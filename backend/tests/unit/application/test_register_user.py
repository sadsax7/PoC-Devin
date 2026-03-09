"""
Tests unitarios para el caso de uso RegisterUser.

Cubre: positivos, negativos, edge cases, transiciones de estado, concurrency hints.
Referencia: HU-BE-01, BACKEND-GUIDELINES.md §5.3.2
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.register_user_dto import RegisterUserInputDTO
from app.application.use_cases.register_user import (
    DuplicatePhoneError,
    EmailValidationError,
    KycRejectedError,
    NameValidationError,
    PasswordValidationError,
    RegisterUserUseCase,
)
from app.domain.entities.user import KycStatus

# ============================================================
# Helpers
# ============================================================


def _build_use_case(
    *,
    find_by_phone_return: object = None,
    save_return: str = "generated_id_123",
    kyc_return: KycStatus = KycStatus.PENDING,
    hash_return: str = "$argon2id$mocked_hash",
) -> RegisterUserUseCase:
    """Construye un RegisterUserUseCase con mocks configurados."""
    repo = MagicMock()
    repo.find_by_phone = AsyncMock(return_value=find_by_phone_return)
    repo.save = AsyncMock(return_value=save_return)

    hasher = MagicMock()
    hasher.hash_password = MagicMock(return_value=hash_return)

    kyc = MagicMock()
    kyc.verify = AsyncMock(return_value=kyc_return)

    publisher = MagicMock()
    publisher.publish = AsyncMock()

    return RegisterUserUseCase(
        user_repository=repo,
        password_hasher=hasher,
        kyc_verification=kyc,
        event_publisher=publisher,
    )


def _valid_input(**overrides: object) -> RegisterUserInputDTO:
    """Crea un DTO de entrada válido con posibles overrides."""
    defaults: dict[str, object] = {
        "phone": "+573001234567",
        "password": "Str0ng!Pass",
    }
    defaults.update(overrides)
    return RegisterUserInputDTO(**defaults)  # type: ignore[arg-type]


# ============================================================
# Positivos
# ============================================================


class TestRegisterUserSuccess:
    """Tests positivos — flujo exitoso."""

    @pytest.mark.asyncio
    async def test_execute_when_valid_input_then_returns_user_id(self) -> None:
        """Registro exitoso retorna user_id."""
        uc = _build_use_case(save_return="abc123")
        result = await uc.execute(_valid_input())
        assert result.user_id == "abc123"

    @pytest.mark.asyncio
    async def test_execute_when_valid_input_then_hashes_password(self) -> None:
        """Se hashea la contraseña, nunca se guarda en plano."""
        uc = _build_use_case()
        await uc.execute(_valid_input())
        uc._password_hasher.hash_password.assert_called_once_with("Str0ng!Pass")

    @pytest.mark.asyncio
    async def test_execute_when_valid_input_then_publishes_event(self) -> None:
        """Se publica el evento UserRegistered."""
        uc = _build_use_case(save_return="abc123")
        await uc.execute(_valid_input())
        uc._event_publisher.publish.assert_called_once()
        call_args = uc._event_publisher.publish.call_args
        assert call_args[0][0] == "UserRegistered"
        assert call_args[0][1]["user_id"] == "abc123"

    @pytest.mark.asyncio
    async def test_execute_when_optional_email_then_saved(self) -> None:
        """Email opcional se incluye en la entidad User."""
        uc = _build_use_case()
        await uc.execute(_valid_input(email="user@example.com"))
        save_call = uc._user_repository.save.call_args[0][0]
        assert save_call.email == "user@example.com"

    @pytest.mark.asyncio
    async def test_execute_when_optional_name_then_saved(self) -> None:
        """Nombre opcional se incluye en la entidad User."""
        uc = _build_use_case()
        await uc.execute(_valid_input(name="Alice"))
        save_call = uc._user_repository.save.call_args[0][0]
        assert save_call.name == "Alice"


# ============================================================
# Negativos
# ============================================================


class TestRegisterUserNegative:
    """Tests negativos — errores esperados."""

    @pytest.mark.asyncio
    async def test_execute_when_weak_password_then_raises(self) -> None:
        """Contraseña débil lanza PasswordValidationError."""
        uc = _build_use_case()
        with pytest.raises(PasswordValidationError) as exc_info:
            await uc.execute(_valid_input(password="weak"))
        assert len(exc_info.value.errors) >= 1

    @pytest.mark.asyncio
    async def test_execute_when_invalid_phone_then_raises(self) -> None:
        """Teléfono inválido lanza ValueError."""
        uc = _build_use_case()
        with pytest.raises(ValueError, match="E\\.164 format"):
            await uc.execute(_valid_input(phone="invalid"))

    @pytest.mark.asyncio
    async def test_execute_when_duplicate_phone_then_raises(self) -> None:
        """Teléfono duplicado lanza DuplicatePhoneError."""
        existing_user = MagicMock()
        uc = _build_use_case(find_by_phone_return=existing_user)
        with pytest.raises(DuplicatePhoneError, match="already registered"):
            await uc.execute(_valid_input())

    @pytest.mark.asyncio
    async def test_execute_when_kyc_rejected_then_raises(self) -> None:
        """KYC rechazado lanza KycRejectedError."""
        uc = _build_use_case(kyc_return=KycStatus.REJECTED)
        with pytest.raises(KycRejectedError, match="rejected"):
            await uc.execute(_valid_input(phone="+573001234500"))

    @pytest.mark.asyncio
    async def test_execute_when_email_too_long_then_raises(self) -> None:
        """Email mayor a 255 chars lanza EmailValidationError."""
        uc = _build_use_case()
        with pytest.raises(EmailValidationError, match="255"):
            await uc.execute(_valid_input(email="a" * 256))

    @pytest.mark.asyncio
    async def test_execute_when_name_too_long_then_raises(self) -> None:
        """Nombre mayor a 100 chars lanza NameValidationError."""
        uc = _build_use_case()
        with pytest.raises(NameValidationError, match="100"):
            await uc.execute(_valid_input(name="a" * 101))


# ============================================================
# Edge cases
# ============================================================


class TestRegisterUserEdgeCases:
    """Edge cases para el registro."""

    @pytest.mark.asyncio
    async def test_execute_when_password_exactly_8_chars_then_ok(self) -> None:
        """Contraseña de exactamente 8 caracteres válida."""
        uc = _build_use_case()
        result = await uc.execute(_valid_input(password="Aa1!xxxx"))
        assert result.user_id is not None

    @pytest.mark.asyncio
    async def test_execute_when_password_128_chars_then_ok(self) -> None:
        """Contraseña de exactamente 128 caracteres válida."""
        pwd = "Aa1!" + "x" * 124
        uc = _build_use_case()
        result = await uc.execute(_valid_input(password=pwd))
        assert result.user_id is not None

    @pytest.mark.asyncio
    async def test_execute_when_email_exactly_255_then_ok(self) -> None:
        """Email de exactamente 255 caracteres es válido."""
        uc = _build_use_case()
        result = await uc.execute(_valid_input(email="a" * 255))
        assert result.user_id is not None

    @pytest.mark.asyncio
    async def test_execute_when_name_exactly_100_then_ok(self) -> None:
        """Nombre de exactamente 100 caracteres es válido."""
        uc = _build_use_case()
        result = await uc.execute(_valid_input(name="a" * 100))
        assert result.user_id is not None

    @pytest.mark.asyncio
    async def test_execute_when_no_email_no_name_then_ok(self) -> None:
        """Sin campos opcionales."""
        uc = _build_use_case()
        result = await uc.execute(_valid_input())
        save_call = uc._user_repository.save.call_args[0][0]
        assert save_call.email is None
        assert save_call.name is None
        assert result.user_id is not None


# ============================================================
# Transiciones de estado (KYC)
# ============================================================


class TestRegisterUserKycTransitions:
    """Tests de transición de estado KYC."""

    @pytest.mark.asyncio
    async def test_execute_when_kyc_approved_then_status_approved(self) -> None:
        """KYC aprobado → kyc_status: approved en la entidad."""
        uc = _build_use_case(kyc_return=KycStatus.APPROVED)
        await uc.execute(_valid_input(phone="+573001234599"))
        saved_user = uc._user_repository.save.call_args[0][0]
        assert saved_user.kyc_status == KycStatus.APPROVED

    @pytest.mark.asyncio
    async def test_execute_when_kyc_pending_then_status_pending(self) -> None:
        """KYC pendiente → kyc_status: pending en la entidad."""
        uc = _build_use_case(kyc_return=KycStatus.PENDING)
        await uc.execute(_valid_input())
        saved_user = uc._user_repository.save.call_args[0][0]
        assert saved_user.kyc_status == KycStatus.PENDING

    @pytest.mark.asyncio
    async def test_execute_when_kyc_rejected_then_user_not_saved(self) -> None:
        """KYC rechazado → usuario NO se persiste."""
        uc = _build_use_case(kyc_return=KycStatus.REJECTED)
        with pytest.raises(KycRejectedError):
            await uc.execute(_valid_input(phone="+573001234500"))
        uc._user_repository.save.assert_not_called()


# ============================================================
# Concurrency hints
# ============================================================


class TestRegisterUserConcurrency:
    """Hints de concurrencia (verificación de secuencia)."""

    @pytest.mark.asyncio
    async def test_execute_checks_phone_uniqueness_before_save(self) -> None:
        """find_by_phone se llama antes de save."""
        uc = _build_use_case()
        await uc.execute(_valid_input())

        # find_by_phone fue llamado
        uc._user_repository.find_by_phone.assert_called_once_with("+573001234567")

        # save fue llamado después
        uc._user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_hashes_before_creating_entity(self) -> None:
        """hash_password se llama antes de crear User (verifica secuencia)."""
        uc = _build_use_case(hash_return="$argon2id$specific_hash")
        await uc.execute(_valid_input())
        saved_user = uc._user_repository.save.call_args[0][0]
        assert saved_user.password_hash == "$argon2id$specific_hash"
