"""
Tests unitarios para el caso de uso LoginUser.

Cubre: positivos, negativos, edge cases, transiciones de estado.
Referencia: HU-BE-02 AC#1, BACKEND-GUIDELINES.md §5.1.7.1
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.auth_dtos import (
    LoginInputDTO,
    LoginMfaRequiredDTO,
    LoginOutputDTO,
)
from app.application.use_cases.login_user import (
    AccountLockedError,
    InvalidCredentialsError,
    LoginUserUseCase,
    UserNotFoundError,
)
from app.domain.entities.user import KycStatus, User

# ============================================================
# Helpers
# ============================================================


def _make_user(
    *,
    user_id: str = "user123",
    phone: str = "+573001234567",
    password_hash: str = "$argon2id$mocked",
    kyc_status: KycStatus = KycStatus.PENDING,
    mfa_enabled: bool = False,
) -> User:
    """Crea una entidad User con valores por defecto."""
    return User(
        id=user_id,
        phone=phone,
        password_hash=password_hash,
        kyc_status=kyc_status,
        mfa_enabled=mfa_enabled,
    )


def _build_use_case(
    *,
    find_by_phone_return: User | None = None,
    verify_password_return: bool = True,
    access_token: str = "mocked.access.token",
    refresh_token: str = "mocked.refresh.token",
    temp_token: str = "mocked.temp.token",
) -> LoginUserUseCase:
    """Construye un LoginUserUseCase con mocks configurados."""
    repo = MagicMock()
    repo.find_by_phone = AsyncMock(return_value=find_by_phone_return)

    hasher = MagicMock()
    hasher.verify_password = MagicMock(return_value=verify_password_return)

    token_provider = MagicMock()
    token_provider.generate_access_token = MagicMock(return_value=access_token)
    token_provider.generate_refresh_token = MagicMock(return_value=refresh_token)
    token_provider.generate_temp_token = MagicMock(return_value=temp_token)

    publisher = MagicMock()
    publisher.publish = AsyncMock()

    return LoginUserUseCase(
        user_repository=repo,
        password_hasher=hasher,
        token_provider=token_provider,
        event_publisher=publisher,
    )


def _valid_input(**overrides: object) -> LoginInputDTO:
    """Crea un DTO de entrada válido."""
    defaults: dict[str, object] = {
        "phone": "+573001234567",
        "password": "Str0ng!Pass",
    }
    defaults.update(overrides)
    return LoginInputDTO(**defaults)  # type: ignore[arg-type]


# ============================================================
# Positivos (happy path)
# ============================================================


class TestLoginUserSuccess:
    """Tests positivos — login exitoso sin MFA."""

    @pytest.mark.asyncio
    async def test_execute_when_valid_credentials_then_returns_tokens(
        self,
    ) -> None:
        """Login exitoso sin MFA retorna access y refresh tokens."""
        user = _make_user(mfa_enabled=False)
        uc = _build_use_case(find_by_phone_return=user)

        result = await uc.execute(_valid_input())

        assert isinstance(result, LoginOutputDTO)
        assert result.access_token == "mocked.access.token"
        assert result.refresh_token == "mocked.refresh.token"
        assert result.token_type == "Bearer"
        assert result.expires_in == 1800

    @pytest.mark.asyncio
    async def test_execute_when_valid_then_publishes_login_success(
        self,
    ) -> None:
        """Se publica evento LoginSuccess."""
        user = _make_user(mfa_enabled=False)
        uc = _build_use_case(find_by_phone_return=user)

        await uc.execute(_valid_input())

        uc._event_publisher.publish.assert_called_once()
        call_args = uc._event_publisher.publish.call_args
        assert call_args[0][0] == "LoginSuccess"
        assert call_args[0][1]["user_id"] == "user123"

    @pytest.mark.asyncio
    async def test_execute_when_valid_then_generates_tokens_with_correct_args(
        self,
    ) -> None:
        """Se generan tokens con user_id y phone correctos."""
        user = _make_user(user_id="uid_99", phone="+573009999999")
        uc = _build_use_case(find_by_phone_return=user)

        await uc.execute(_valid_input(phone="+573009999999"))

        uc._token_provider.generate_access_token.assert_called_once_with("uid_99", "+573009999999")
        uc._token_provider.generate_refresh_token.assert_called_once_with("uid_99")


# ============================================================
# MFA Required
# ============================================================


class TestLoginUserMfaRequired:
    """Tests — login con MFA habilitado."""

    @pytest.mark.asyncio
    async def test_execute_when_mfa_enabled_then_returns_mfa_dto(
        self,
    ) -> None:
        """Login con MFA habilitado retorna LoginMfaRequiredDTO."""
        user = _make_user(mfa_enabled=True)
        uc = _build_use_case(find_by_phone_return=user)

        result = await uc.execute(_valid_input())

        assert isinstance(result, LoginMfaRequiredDTO)
        assert result.temp_token == "mocked.temp.token"
        assert result.mfa_required is True

    @pytest.mark.asyncio
    async def test_execute_when_mfa_then_publishes_mfa_event(self) -> None:
        """Se publica evento LoginMfaRequired."""
        user = _make_user(mfa_enabled=True)
        uc = _build_use_case(find_by_phone_return=user)

        await uc.execute(_valid_input())

        call_args = uc._event_publisher.publish.call_args
        assert call_args[0][0] == "LoginMfaRequired"

    @pytest.mark.asyncio
    async def test_execute_when_mfa_then_no_access_refresh_tokens(
        self,
    ) -> None:
        """Cuando MFA es requerido, NO se generan access/refresh tokens."""
        user = _make_user(mfa_enabled=True)
        uc = _build_use_case(find_by_phone_return=user)

        await uc.execute(_valid_input())

        uc._token_provider.generate_access_token.assert_not_called()
        uc._token_provider.generate_refresh_token.assert_not_called()
        uc._token_provider.generate_temp_token.assert_called_once_with("user123")


# ============================================================
# Negativos (error handling)
# ============================================================


class TestLoginUserNegative:
    """Tests negativos — errores esperados."""

    @pytest.mark.asyncio
    async def test_execute_when_phone_not_found_then_raises(self) -> None:
        """Teléfono no registrado lanza UserNotFoundError."""
        uc = _build_use_case(find_by_phone_return=None)

        with pytest.raises(UserNotFoundError, match="not registered"):
            await uc.execute(_valid_input())

    @pytest.mark.asyncio
    async def test_execute_when_wrong_password_then_raises(self) -> None:
        """Contraseña incorrecta lanza InvalidCredentialsError."""
        user = _make_user()
        uc = _build_use_case(
            find_by_phone_return=user,
            verify_password_return=False,
        )

        with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
            await uc.execute(_valid_input())

    @pytest.mark.asyncio
    async def test_execute_when_kyc_rejected_then_raises(self) -> None:
        """Cuenta con KYC rechazado lanza AccountLockedError."""
        user = _make_user(kyc_status=KycStatus.REJECTED)
        uc = _build_use_case(find_by_phone_return=user)

        with pytest.raises(AccountLockedError, match="locked"):
            await uc.execute(_valid_input())

    @pytest.mark.asyncio
    async def test_execute_when_kyc_rejected_then_doesnt_check_password(
        self,
    ) -> None:
        """Si KYC rechazado, no se verifica contraseña."""
        user = _make_user(kyc_status=KycStatus.REJECTED)
        uc = _build_use_case(find_by_phone_return=user)

        with pytest.raises(AccountLockedError):
            await uc.execute(_valid_input())

        uc._password_hasher.verify_password.assert_not_called()


# ============================================================
# Edge cases
# ============================================================


class TestLoginUserEdgeCases:
    """Edge cases para login."""

    @pytest.mark.asyncio
    async def test_execute_when_user_id_none_then_uses_empty_string(
        self,
    ) -> None:
        """Si user.id es None, se usa cadena vacía como user_id."""
        user = _make_user(mfa_enabled=False)
        user.id = None
        uc = _build_use_case(find_by_phone_return=user)

        result = await uc.execute(_valid_input())

        assert isinstance(result, LoginOutputDTO)
        uc._token_provider.generate_access_token.assert_called_once_with("", "+573001234567")

    @pytest.mark.asyncio
    async def test_execute_when_kyc_approved_then_login_succeeds(
        self,
    ) -> None:
        """KYC aprobado permite login."""
        user = _make_user(kyc_status=KycStatus.APPROVED, mfa_enabled=False)
        uc = _build_use_case(find_by_phone_return=user)

        result = await uc.execute(_valid_input())

        assert isinstance(result, LoginOutputDTO)

    @pytest.mark.asyncio
    async def test_execute_when_kyc_pending_then_login_succeeds(
        self,
    ) -> None:
        """KYC pendiente permite login."""
        user = _make_user(kyc_status=KycStatus.PENDING, mfa_enabled=False)
        uc = _build_use_case(find_by_phone_return=user)

        result = await uc.execute(_valid_input())

        assert isinstance(result, LoginOutputDTO)


# ============================================================
# Secuencia de operaciones
# ============================================================


class TestLoginUserSequence:
    """Verificación del orden de operaciones."""

    @pytest.mark.asyncio
    async def test_execute_checks_kyc_before_password(self) -> None:
        """KYC se verifica antes que la contraseña."""
        user = _make_user(kyc_status=KycStatus.REJECTED)
        uc = _build_use_case(find_by_phone_return=user)

        with pytest.raises(AccountLockedError):
            await uc.execute(_valid_input())

        uc._password_hasher.verify_password.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_verifies_password_with_correct_args(self) -> None:
        """verify_password recibe plain_password y hash."""
        user = _make_user(password_hash="$argon2id$the_hash")
        uc = _build_use_case(find_by_phone_return=user)

        await uc.execute(_valid_input(password="MyPass123!"))

        uc._password_hasher.verify_password.assert_called_once_with(
            "MyPass123!", "$argon2id$the_hash"
        )
