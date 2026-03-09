"""
Tests unitarios para auth_router (register, login, MFA — sin DB).

Usa dependency overrides para inyectar mocks directamente.
Referencia: HU-BE-01 AC#7, HU-BE-02 AC#1-3
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.adapters.inbound.http.dependencies.container import (
    get_login_user_use_case,
    get_register_user_use_case,
    get_verify_mfa_use_case,
)
from app.application.dtos.auth_dtos import (
    LoginMfaRequiredDTO,
    LoginOutputDTO,
    VerifyMfaOutputDTO,
)
from app.application.use_cases.login_user import (
    AccountLockedError,
    InvalidCredentialsError,
    LoginUserUseCase,
    UserNotFoundError,
)
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.verify_mfa import (
    InvalidMfaCodeError,
    InvalidTempTokenError,
    TooManyMfaAttemptsError,
    VerifyMfaUseCase,
)
from app.domain.entities.user import KycStatus
from main import app

# ============================================================
# Helpers
# ============================================================


def _valid_body(**overrides: object) -> dict[str, object]:
    defaults: dict[str, object] = {
        "phone": "+573001234567",
        "password": "Str0ng!Pass",
    }
    defaults.update(overrides)
    return defaults


def _mock_use_case(
    *,
    find_by_phone_return: object = None,
    save_return: str = "507f1f77bcf86cd799439011",
    kyc_return: KycStatus = KycStatus.PENDING,
) -> RegisterUserUseCase:
    """Crea un RegisterUserUseCase con mocks inyectados."""
    repo = MagicMock()
    repo.find_by_phone = AsyncMock(return_value=find_by_phone_return)
    repo.save = AsyncMock(return_value=save_return)

    hasher = MagicMock()
    hasher.hash_password = MagicMock(return_value="$argon2id$hash")

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


# ============================================================
# Positivos
# ============================================================


class TestAuthRouterSuccess:
    """Tests HTTP positivos usando dependency overrides."""

    @pytest.mark.asyncio
    async def test_register_when_valid_then_201(self) -> None:
        """Registro exitoso retorna 201 con user_id."""
        uc = _mock_use_case()
        app.dependency_overrides[get_register_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post("/auth/register", json=_valid_body())
            assert resp.status_code == 201
            assert resp.json()["user_id"] == "507f1f77bcf86cd799439011"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_when_with_optional_fields_then_201(self) -> None:
        """Registro con email y name retorna 201."""
        uc = _mock_use_case()
        app.dependency_overrides[get_register_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/register",
                    json=_valid_body(email="user@test.com", name="Alice"),
                )
            assert resp.status_code == 201
        finally:
            app.dependency_overrides.clear()


# ============================================================
# Negativos (códigos HTTP de error)
# ============================================================


class TestAuthRouterErrors:
    """Tests HTTP negativos via dependency overrides."""

    @pytest.mark.asyncio
    async def test_register_when_duplicate_phone_then_409(self) -> None:
        """Teléfono duplicado retorna 409 Conflict."""
        uc = _mock_use_case(find_by_phone_return=MagicMock())
        app.dependency_overrides[get_register_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post("/auth/register", json=_valid_body())
            assert resp.status_code == 409
            assert "already registered" in resp.json()["detail"]
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_when_kyc_rejected_then_400(self) -> None:
        """KYC rechazado retorna 400."""
        uc = _mock_use_case(kyc_return=KycStatus.REJECTED)
        app.dependency_overrides[get_register_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/register",
                    json=_valid_body(phone="+573001234500"),
                )
            assert resp.status_code == 400
            assert "rejected" in resp.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_when_weak_password_then_422(self) -> None:
        """Contraseña débil retorna 422 con detalle de errores."""
        uc = _mock_use_case()
        app.dependency_overrides[get_register_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/register",
                    json=_valid_body(password="weak"),
                )
            assert resp.status_code == 422
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_when_invalid_phone_format_then_422(self) -> None:
        """Teléfono con formato inválido retorna 422."""
        uc = _mock_use_case()
        app.dependency_overrides[get_register_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/register",
                    json=_valid_body(phone="invalid_phone"),
                )
            assert resp.status_code == 422
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_when_missing_phone_then_422(self) -> None:
        """Sin campo phone retorna 422 (validación Pydantic)."""
        uc = _mock_use_case()
        app.dependency_overrides[get_register_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/register",
                    json={"password": "Str0ng!Pass"},
                )
            assert resp.status_code == 422
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_register_when_missing_password_then_422(self) -> None:
        """Sin campo password retorna 422 (validación Pydantic)."""
        uc = _mock_use_case()
        app.dependency_overrides[get_register_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/register",
                    json={"phone": "+573001234567"},
                )
            assert resp.status_code == 422
        finally:
            app.dependency_overrides.clear()


# ============================================================
# Login endpoint helpers
# ============================================================


def _login_body(**overrides: object) -> dict[str, object]:
    """Crea cuerpo de login por defecto."""
    defaults: dict[str, object] = {
        "phone": "+573001234567",
        "password": "Str0ng!Pass",
    }
    defaults.update(overrides)
    return defaults


def _mock_login_use_case(
    *,
    return_value: LoginOutputDTO | LoginMfaRequiredDTO | None = None,
    side_effect: Exception | None = None,
) -> MagicMock:
    """Crea un mock de LoginUserUseCase."""
    mock = MagicMock(spec=LoginUserUseCase)
    if side_effect is not None:
        mock.execute = AsyncMock(side_effect=side_effect)
    else:
        if return_value is None:
            return_value = LoginOutputDTO(
                access_token="test.access.token",
                refresh_token="test.refresh.token",
            )
        mock.execute = AsyncMock(return_value=return_value)
    return mock


def _mock_verify_mfa_use_case(
    *,
    return_value: VerifyMfaOutputDTO | None = None,
    side_effect: Exception | None = None,
) -> MagicMock:
    """Crea un mock de VerifyMfaUseCase."""
    mock = MagicMock(spec=VerifyMfaUseCase)
    if side_effect is not None:
        mock.execute = AsyncMock(side_effect=side_effect)
    else:
        if return_value is None:
            return_value = VerifyMfaOutputDTO(
                access_token="mfa.access.token",
                refresh_token="mfa.refresh.token",
            )
        mock.execute = AsyncMock(return_value=return_value)
    return mock


# ============================================================
# Login — Positivos
# ============================================================


class TestLoginRouterSuccess:
    """Tests HTTP positivos para POST /auth/login."""

    @pytest.mark.asyncio
    async def test_login_when_valid_then_200_with_tokens(self) -> None:
        """Login exitoso retorna 200 con access y refresh tokens."""
        uc = _mock_login_use_case()
        app.dependency_overrides[get_login_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post("/auth/login", json=_login_body())
            assert resp.status_code == 200
            body = resp.json()
            assert body["access_token"] == "test.access.token"
            assert body["refresh_token"] == "test.refresh.token"
            assert body["token_type"] == "Bearer"
            assert body["expires_in"] == 1800
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_when_mfa_required_then_200_with_temp_token(
        self,
    ) -> None:
        """Login con MFA retorna 200 con temp_token y mfa_required=true."""
        mfa_dto = LoginMfaRequiredDTO(temp_token="test.temp.token")
        uc = _mock_login_use_case(return_value=mfa_dto)
        app.dependency_overrides[get_login_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post("/auth/login", json=_login_body())
            assert resp.status_code == 200
            body = resp.json()
            assert body["temp_token"] == "test.temp.token"
            assert body["mfa_required"] is True
        finally:
            app.dependency_overrides.clear()


# ============================================================
# Login — Negativos
# ============================================================


class TestLoginRouterErrors:
    """Tests HTTP negativos para POST /auth/login."""

    @pytest.mark.asyncio
    async def test_login_when_user_not_found_then_401(self) -> None:
        """Teléfono no registrado retorna 401."""
        uc = _mock_login_use_case(
            side_effect=UserNotFoundError("Phone number not registered"),
        )
        app.dependency_overrides[get_login_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post("/auth/login", json=_login_body())
            assert resp.status_code == 401
            assert "Invalid credentials" in resp.json()["detail"]
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_when_wrong_password_then_401(self) -> None:
        """Contraseña incorrecta retorna 401."""
        uc = _mock_login_use_case(
            side_effect=InvalidCredentialsError("Invalid credentials"),
        )
        app.dependency_overrides[get_login_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post("/auth/login", json=_login_body())
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_when_account_locked_then_423(self) -> None:
        """Cuenta bloqueada retorna 423 Locked."""
        uc = _mock_login_use_case(
            side_effect=AccountLockedError("Account locked"),
        )
        app.dependency_overrides[get_login_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post("/auth/login", json=_login_body())
            assert resp.status_code == 423
            assert "locked" in resp.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_when_missing_phone_then_422(self) -> None:
        """Sin campo phone retorna 422."""
        uc = _mock_login_use_case()
        app.dependency_overrides[get_login_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/login",
                    json={"password": "Str0ng!Pass"},
                )
            assert resp.status_code == 422
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_when_missing_password_then_422(self) -> None:
        """Sin campo password retorna 422."""
        uc = _mock_login_use_case()
        app.dependency_overrides[get_login_user_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/login",
                    json={"phone": "+573001234567"},
                )
            assert resp.status_code == 422
        finally:
            app.dependency_overrides.clear()


# ============================================================
# MFA Verify — Positivos
# ============================================================


class TestMfaVerifyRouterSuccess:
    """Tests HTTP positivos para POST /auth/mfa/verify."""

    @pytest.mark.asyncio
    async def test_mfa_verify_when_valid_then_200_with_tokens(self) -> None:
        """Verificación MFA exitosa retorna 200 con tokens."""
        uc = _mock_verify_mfa_use_case()
        app.dependency_overrides[get_verify_mfa_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/mfa/verify",
                    json={"temp_token": "valid.token", "code": "123456"},
                )
            assert resp.status_code == 200
            body = resp.json()
            assert body["access_token"] == "mfa.access.token"
            assert body["refresh_token"] == "mfa.refresh.token"
            assert body["token_type"] == "Bearer"
        finally:
            app.dependency_overrides.clear()


# ============================================================
# MFA Verify — Negativos
# ============================================================


class TestMfaVerifyRouterErrors:
    """Tests HTTP negativos para POST /auth/mfa/verify."""

    @pytest.mark.asyncio
    async def test_mfa_verify_when_invalid_temp_token_then_401(self) -> None:
        """Token temporal inválido retorna 401."""
        uc = _mock_verify_mfa_use_case(
            side_effect=InvalidTempTokenError("expired"),
        )
        app.dependency_overrides[get_verify_mfa_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/mfa/verify",
                    json={"temp_token": "expired.token", "code": "123456"},
                )
            assert resp.status_code == 401
            assert "expired" in resp.json()["detail"].lower()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_mfa_verify_when_wrong_code_then_401(self) -> None:
        """Código MFA incorrecto retorna 401 con intentos restantes."""
        uc = _mock_verify_mfa_use_case(
            side_effect=InvalidMfaCodeError(attempts_remaining=2),
        )
        app.dependency_overrides[get_verify_mfa_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/mfa/verify",
                    json={"temp_token": "valid.token", "code": "000000"},
                )
            assert resp.status_code == 401
            assert "2 attempts remaining" in resp.json()["detail"]
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_mfa_verify_when_too_many_attempts_then_429(self) -> None:
        """Demasiados intentos retorna 429."""
        uc = _mock_verify_mfa_use_case(
            side_effect=TooManyMfaAttemptsError("Too many"),
        )
        app.dependency_overrides[get_verify_mfa_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/mfa/verify",
                    json={"temp_token": "valid.token", "code": "123456"},
                )
            assert resp.status_code == 429
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_mfa_verify_when_missing_code_then_422(self) -> None:
        """Sin campo code retorna 422."""
        uc = _mock_verify_mfa_use_case()
        app.dependency_overrides[get_verify_mfa_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/mfa/verify",
                    json={"temp_token": "valid.token"},
                )
            assert resp.status_code == 422
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_mfa_verify_when_code_too_short_then_422(self) -> None:
        """Código menor a 6 dígitos retorna 422."""
        uc = _mock_verify_mfa_use_case()
        app.dependency_overrides[get_verify_mfa_use_case] = lambda: uc

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/mfa/verify",
                    json={"temp_token": "valid.token", "code": "123"},
                )
            assert resp.status_code == 422
        finally:
            app.dependency_overrides.clear()
