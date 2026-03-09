"""
Tests de integración para endpoints de auth (register, login, MFA).

Usa httpx.AsyncClient contra la app FastAPI con dependency_overrides.
Referencia: HU-BE-01 AC#7, HU-BE-02 AC#1-3, DoD#10
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
    """Genera body válido con posibles overrides."""
    body: dict[str, object] = {
        "phone": "+573001234567",
        "password": "Str0ng!Pass",
    }
    body.update(overrides)
    return body


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


class TestAuthRegisterEndpoint:
    """Tests HTTP para POST /auth/register."""

    @pytest.mark.asyncio
    async def test_register_when_valid_then_201(self) -> None:
        """POST /auth/register con datos válidos retorna 201."""
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
    async def test_register_when_with_email_name_then_201(self) -> None:
        """POST con email y name opcionales retorna 201."""
        uc = _mock_use_case()
        app.dependency_overrides[get_register_user_use_case] = lambda: uc
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/register",
                    json=_valid_body(email="user@example.com", name="Alice"),
                )
            assert resp.status_code == 201
        finally:
            app.dependency_overrides.clear()


# ============================================================
# Negativos
# ============================================================


class TestAuthRegisterErrors:
    """Tests de errores HTTP."""

    @pytest.mark.asyncio
    async def test_register_when_duplicate_phone_then_409(self) -> None:
        """Teléfono duplicado retorna 409."""
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
        """Contraseña débil retorna 422."""
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
    async def test_register_when_missing_phone_then_422(self) -> None:
        """Body sin phone retorna 422 (validación Pydantic)."""
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


# ============================================================
# Login Integration Tests
# ============================================================


def _mock_login_uc(
    *,
    return_value: LoginOutputDTO | LoginMfaRequiredDTO | None = None,
    side_effect: Exception | None = None,
) -> MagicMock:
    """Crea un mock para LoginUserUseCase."""
    mock = MagicMock(spec=LoginUserUseCase)
    if side_effect:
        mock.execute = AsyncMock(side_effect=side_effect)
    else:
        if return_value is None:
            return_value = LoginOutputDTO(
                access_token="int.access.token",
                refresh_token="int.refresh.token",
            )
        mock.execute = AsyncMock(return_value=return_value)
    return mock


def _mock_mfa_uc(
    *,
    return_value: VerifyMfaOutputDTO | None = None,
    side_effect: Exception | None = None,
) -> MagicMock:
    """Crea un mock para VerifyMfaUseCase."""
    mock = MagicMock(spec=VerifyMfaUseCase)
    if side_effect:
        mock.execute = AsyncMock(side_effect=side_effect)
    else:
        if return_value is None:
            return_value = VerifyMfaOutputDTO(
                access_token="mfa.access.token",
                refresh_token="mfa.refresh.token",
            )
        mock.execute = AsyncMock(return_value=return_value)
    return mock


class TestLoginEndpoint:
    """Tests de integración para POST /auth/login."""

    @pytest.mark.asyncio
    async def test_login_when_valid_then_200_with_tokens(self) -> None:
        """Login exitoso retorna 200 con tokens JWT."""
        uc = _mock_login_uc()
        app.dependency_overrides[get_login_user_use_case] = lambda: uc
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/login",
                    json={"phone": "+573001234567", "password": "Str0ng!Pass"},
                )
            assert resp.status_code == 200
            body = resp.json()
            assert body["access_token"] == "int.access.token"
            assert body["token_type"] == "Bearer"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_when_mfa_then_200_with_temp_token(self) -> None:
        """Login con MFA retorna 200 con temp_token."""
        mfa_dto = LoginMfaRequiredDTO(temp_token="int.temp.token")
        uc = _mock_login_uc(return_value=mfa_dto)
        app.dependency_overrides[get_login_user_use_case] = lambda: uc
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/login",
                    json={"phone": "+573001234567", "password": "Str0ng!Pass"},
                )
            assert resp.status_code == 200
            body = resp.json()
            assert body["temp_token"] == "int.temp.token"
            assert body["mfa_required"] is True
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_when_not_found_then_401(self) -> None:
        """Teléfono no registrado → 401."""
        uc = _mock_login_uc(side_effect=UserNotFoundError("not found"))
        app.dependency_overrides[get_login_user_use_case] = lambda: uc
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/login",
                    json={"phone": "+573001234567", "password": "Str0ng!Pass"},
                )
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_when_wrong_password_then_401(self) -> None:
        """Contraseña incorrecta → 401."""
        uc = _mock_login_uc(side_effect=InvalidCredentialsError("wrong"))
        app.dependency_overrides[get_login_user_use_case] = lambda: uc
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/login",
                    json={"phone": "+573001234567", "password": "Wrong!Pass1"},
                )
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_login_when_locked_then_423(self) -> None:
        """Cuenta bloqueada → 423."""
        uc = _mock_login_uc(side_effect=AccountLockedError("locked"))
        app.dependency_overrides[get_login_user_use_case] = lambda: uc
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/login",
                    json={"phone": "+573001234567", "password": "Str0ng!Pass"},
                )
            assert resp.status_code == 423
        finally:
            app.dependency_overrides.clear()


class TestMfaVerifyEndpoint:
    """Tests de integración para POST /auth/mfa/verify."""

    @pytest.mark.asyncio
    async def test_mfa_verify_when_valid_then_200(self) -> None:
        """Verificación MFA exitosa retorna 200 con tokens."""
        uc = _mock_mfa_uc()
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
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_mfa_verify_when_expired_token_then_401(self) -> None:
        """Token expirado → 401."""
        uc = _mock_mfa_uc(side_effect=InvalidTempTokenError("expired"))
        app.dependency_overrides[get_verify_mfa_use_case] = lambda: uc
        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.post(
                    "/auth/mfa/verify",
                    json={"temp_token": "expired.token", "code": "123456"},
                )
            assert resp.status_code == 401
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_mfa_verify_when_wrong_code_then_401(self) -> None:
        """Código MFA incorrecto → 401."""
        uc = _mock_mfa_uc(
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
        """Demasiados intentos → 429."""
        uc = _mock_mfa_uc(side_effect=TooManyMfaAttemptsError("blocked"))
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
