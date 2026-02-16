"""Tests de integracion para los endpoints POST /auth/login y POST /auth/mfa/verify.

Verifica el flujo completo de login y verificacion MFA a traves del router HTTP,
incluyendo validacion, manejo de errores y flujo completo Login -> MFA -> Tokens.
"""

from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.application.dtos.login_user_dto import LoginUserOutputDTO
from app.application.dtos.verify_mfa_dto import VerifyMfaOutputDTO
from app.application.use_cases.login_user_use_case import (
    AccountLockedError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.application.use_cases.verify_mfa_use_case import (
    InvalidMfaCodeError,
    TempTokenExpiredError,
    TooManyMfaAttemptsError,
)
from app.infrastructure.api.app import create_app


@pytest_asyncio.fixture
async def app() -> AsyncIterator[FastAPI]:
    """Crea una instancia de la aplicacion para testing."""
    with patch("app.infrastructure.api.app.connect_mongo", new_callable=AsyncMock):
        with patch("app.infrastructure.api.app.disconnect_mongo", new_callable=AsyncMock):
            with patch("app.infrastructure.api.app.get_database") as mock_db:
                mock_db.return_value = MagicMock()
                with patch("app.infrastructure.api.app.MongoUserRepository") as mock_repo_cls:
                    mock_repo_cls.return_value.ensure_indexes = AsyncMock()
                    application = create_app()
                    async with application.router.lifespan_context(application):
                        yield application


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Crea un cliente HTTP asincrono para testing."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_login_when_valid_credentials_no_mfa_then_returns_tokens(
    client: AsyncClient,
) -> None:
    """Integracion positiva: login exitoso sin MFA retorna tokens."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_login_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = LoginUserOutputDTO(
            mfa_required=False,
            access_token="eyJ.access.token",
            refresh_token="eyJ.refresh.token",
            token_type="Bearer",
            expires_in=1800,
        )
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/login",
            json={"phone": "+573001234567", "password": "ValidPass1!"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "eyJ.access.token"
    assert data["refresh_token"] == "eyJ.refresh.token"
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 1800


@pytest.mark.asyncio
async def test_login_when_mfa_enabled_then_returns_temp_token(
    client: AsyncClient,
) -> None:
    """Integracion positiva: login con MFA retorna temp_token."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_login_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = LoginUserOutputDTO(
            mfa_required=True,
            temp_token="eyJ.temp.token",
            message="MFA verification required",
        )
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/login",
            json={"phone": "+573001234567", "password": "ValidPass1!"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["temp_token"] == "eyJ.temp.token"
    assert data["mfa_required"] is True
    assert data["message"] == "MFA verification required"


@pytest.mark.asyncio
async def test_login_when_phone_not_found_then_returns_404(
    client: AsyncClient,
) -> None:
    """Integracion negativa: telefono no registrado retorna 404."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_login_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = UserNotFoundError("Phone number not registered")
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/login",
            json={"phone": "+573009999999", "password": "ValidPass1!"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Phone number not registered"


@pytest.mark.asyncio
async def test_login_when_wrong_password_then_returns_401(
    client: AsyncClient,
) -> None:
    """Integracion negativa: contrasena incorrecta retorna 401."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_login_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = InvalidCredentialsError("Invalid credentials")
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/login",
            json={"phone": "+573001234567", "password": "WrongPass1!"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
async def test_login_when_account_locked_then_returns_423(
    client: AsyncClient,
) -> None:
    """Integracion negativa: cuenta bloqueada retorna 423."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_login_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = AccountLockedError("Account locked due to KYC rejection")
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/login",
            json={"phone": "+573001234567", "password": "ValidPass1!"},
        )

    assert response.status_code == 423
    assert response.json()["detail"] == "Account locked due to KYC rejection"


@pytest.mark.asyncio
async def test_login_when_password_too_short_then_returns_422(
    client: AsyncClient,
) -> None:
    """Edge case: contrasena menor a 8 caracteres retorna 422 por Pydantic."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"phone": "+573001234567", "password": "short"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_when_missing_phone_then_returns_422(
    client: AsyncClient,
) -> None:
    """Edge case: payload sin phone retorna 422."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"password": "ValidPass1!"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_when_empty_body_then_returns_422(
    client: AsyncClient,
) -> None:
    """Edge case: body vacio retorna 422."""
    response = await client.post("/api/v1/auth/login", json={})

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_mfa_verify_when_correct_code_then_returns_tokens(
    client: AsyncClient,
) -> None:
    """Integracion positiva: codigo MFA correcto retorna tokens."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_verify_mfa_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = VerifyMfaOutputDTO(
            access_token="eyJ.access.final",
            refresh_token="eyJ.refresh.final",
            token_type="Bearer",
            expires_in=1800,
        )
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"temp_token": "eyJ.temp.token", "code": "123456"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "eyJ.access.final"
    assert data["refresh_token"] == "eyJ.refresh.final"
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 1800


@pytest.mark.asyncio
async def test_mfa_verify_when_wrong_code_then_returns_401(
    client: AsyncClient,
) -> None:
    """Integracion negativa: codigo MFA incorrecto retorna 401."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_verify_mfa_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = InvalidMfaCodeError(attempts_remaining=2)
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"temp_token": "eyJ.temp.token", "code": "000000"},
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_mfa_verify_when_expired_token_then_returns_401(
    client: AsyncClient,
) -> None:
    """Integracion negativa: token temporal expirado retorna 401."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_verify_mfa_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = TempTokenExpiredError(
            "Temporary token expired, please login again"
        )
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"temp_token": "eyJ.expired.token", "code": "123456"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Temporary token expired, please login again"


@pytest.mark.asyncio
async def test_mfa_verify_when_too_many_attempts_then_returns_429(
    client: AsyncClient,
) -> None:
    """Integracion negativa: demasiados intentos retorna 429."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_verify_mfa_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = TooManyMfaAttemptsError(
            "Too many failed MFA attempts, please login again"
        )
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"temp_token": "eyJ.temp.token", "code": "000000"},
        )

    assert response.status_code == 429
    assert response.json()["detail"] == "Too many failed MFA attempts, please login again"


@pytest.mark.asyncio
async def test_mfa_verify_when_code_too_short_then_returns_422(
    client: AsyncClient,
) -> None:
    """Edge case: codigo menor a 6 digitos retorna 422."""
    response = await client.post(
        "/api/v1/auth/mfa/verify",
        json={"temp_token": "eyJ.temp.token", "code": "123"},
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_then_mfa_verify_full_flow(
    client: AsyncClient,
) -> None:
    """Integracion: flujo completo Login -> MFA -> Access Token."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_login_user_use_case"
    ) as mock_login_factory:
        mock_login_uc = AsyncMock()
        mock_login_uc.execute.return_value = LoginUserOutputDTO(
            mfa_required=True,
            temp_token="eyJ.temp.for.mfa",
            message="MFA verification required",
        )
        mock_login_factory.return_value = mock_login_uc

        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"phone": "+573001234567", "password": "ValidPass1!"},
        )

    assert login_resp.status_code == 200
    temp_token = login_resp.json()["temp_token"]

    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_verify_mfa_use_case"
    ) as mock_mfa_factory:
        mock_mfa_uc = AsyncMock()
        mock_mfa_uc.execute.return_value = VerifyMfaOutputDTO(
            access_token="eyJ.final.access",
            refresh_token="eyJ.final.refresh",
            token_type="Bearer",
            expires_in=1800,
        )
        mock_mfa_factory.return_value = mock_mfa_uc

        mfa_resp = await client.post(
            "/api/v1/auth/mfa/verify",
            json={"temp_token": temp_token, "code": "123456"},
        )

    assert mfa_resp.status_code == 200
    data = mfa_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_login_state_transition_when_rejected_to_locked_then_423(
    client: AsyncClient,
) -> None:
    """Estado: usuario con KYC rejected no puede hacer login."""
    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_login_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = AccountLockedError("Account locked due to KYC rejection")
        mock_factory.return_value = mock_uc

        response = await client.post(
            "/api/v1/auth/login",
            json={"phone": "+573001234567", "password": "ValidPass1!"},
        )

    assert response.status_code == 423
