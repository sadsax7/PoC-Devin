"""Tests de integracion para el endpoint GET /users/me.

Verifica el flujo completo de obtencion del perfil de usuario autenticado,
incluyendo validacion de tokens, manejo de errores y sanitizacion de respuesta.
"""

import asyncio
from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.adapters.inbound.http.dependencies.auth import get_current_user
from app.application.dtos.user_profile_dto import UserProfileOutputDTO
from app.application.use_cases.get_user_profile_use_case import UserNotFoundError
from app.domain.ports.token_provider_port import (
    TokenExpiredException,
    TokenInvalidException,
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
async def test_users_me_when_valid_token_then_returns_profile(
    app: FastAPI,
    client: AsyncClient,
) -> None:
    """Integracion positiva: token valido retorna perfil sanitizado."""
    profile = UserProfileOutputDTO(
        user_id="507f1f77bcf86cd799439011",
        phone="+573001234567",
        email="user@example.com",
        name="Juan Perez",
        kyc_status="pending",
        mfa_enabled=False,
        created_at="2026-01-30T14:23:45.123Z",
    )
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = profile

    async def override_auth() -> str:
        return "507f1f77bcf86cd799439011"

    app.dependency_overrides[get_current_user] = override_auth
    try:
        with patch(
            "app.adapters.inbound.http.routers.users_router.get_user_profile_use_case",
            return_value=mock_uc,
        ):
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer valid.access.token"},
            )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "507f1f77bcf86cd799439011"
    assert data["phone"] == "+573001234567"
    assert data["email"] == "user@example.com"
    assert data["name"] == "Juan Perez"
    assert data["kyc_status"] == "pending"
    assert data["mfa_enabled"] is False
    assert data["created_at"] == "2026-01-30T14:23:45.123Z"


@pytest.mark.asyncio
async def test_users_me_when_valid_token_then_excludes_password_hash(
    app: FastAPI,
    client: AsyncClient,
) -> None:
    """Seguridad: respuesta NO contiene password_hash ni mfa_secret."""
    profile = UserProfileOutputDTO(
        user_id="507f1f77bcf86cd799439011",
        phone="+573001234567",
        email="user@example.com",
        name="Juan Perez",
        kyc_status="approved",
        mfa_enabled=True,
        created_at="2026-01-30T14:23:45.123Z",
    )
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = profile

    async def override_auth() -> str:
        return "507f1f77bcf86cd799439011"

    app.dependency_overrides[get_current_user] = override_auth
    try:
        with patch(
            "app.adapters.inbound.http.routers.users_router.get_user_profile_use_case",
            return_value=mock_uc,
        ):
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer valid.access.token"},
            )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert "password_hash" not in data
    assert "mfa_secret" not in data


@pytest.mark.asyncio
async def test_users_me_when_no_auth_header_then_returns_401(
    client: AsyncClient,
) -> None:
    """Integracion negativa: sin header Authorization retorna 401."""
    response = await client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authorization token"


@pytest.mark.asyncio
async def test_users_me_when_invalid_token_then_returns_401(
    client: AsyncClient,
) -> None:
    """Integracion negativa: token invalido retorna 401."""
    with patch("app.adapters.inbound.http.dependencies.auth._get_token_provider") as mock_tp:
        mock_provider = MagicMock()
        mock_provider.decode_token.side_effect = TokenInvalidException("Invalid token: bad")
        mock_tp.return_value = mock_provider

        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token signature"


@pytest.mark.asyncio
async def test_users_me_when_expired_token_then_returns_401(
    client: AsyncClient,
) -> None:
    """Integracion negativa: token expirado retorna 401."""
    with patch("app.adapters.inbound.http.dependencies.auth._get_token_provider") as mock_tp:
        mock_provider = MagicMock()
        mock_provider.decode_token.side_effect = TokenExpiredException("Token has expired")
        mock_tp.return_value = mock_provider

        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer expired.token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"


@pytest.mark.asyncio
async def test_users_me_when_refresh_token_then_returns_401(
    client: AsyncClient,
) -> None:
    """Integracion negativa: refresh token rechazado."""
    with patch("app.adapters.inbound.http.dependencies.auth._get_token_provider") as mock_tp:
        mock_provider = MagicMock()
        mock_provider.decode_token.return_value = {
            "sub": "507f1f77bcf86cd799439011",
            "type": "refresh",
        }
        mock_tp.return_value = mock_provider

        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer refresh.token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token type, access token required"


@pytest.mark.asyncio
async def test_users_me_when_temp_token_then_returns_401(
    client: AsyncClient,
) -> None:
    """Integracion negativa: temp token rechazado."""
    with patch("app.adapters.inbound.http.dependencies.auth._get_token_provider") as mock_tp:
        mock_provider = MagicMock()
        mock_provider.decode_token.return_value = {
            "sub": "507f1f77bcf86cd799439011",
            "type": "temp",
        }
        mock_tp.return_value = mock_provider

        response = await client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer temp.token"},
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token type, access token required"


@pytest.mark.asyncio
async def test_users_me_when_user_not_found_then_returns_404(
    app: FastAPI,
    client: AsyncClient,
) -> None:
    """Integracion negativa: usuario eliminado despues de login retorna 404."""
    mock_uc = AsyncMock()
    mock_uc.execute.side_effect = UserNotFoundError("User not found")

    async def override_auth() -> str:
        return "507f1f77bcf86cd799439011"

    app.dependency_overrides[get_current_user] = override_auth
    try:
        with patch(
            "app.adapters.inbound.http.routers.users_router.get_user_profile_use_case",
            return_value=mock_uc,
        ):
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer valid.access.token"},
            )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.asyncio
async def test_users_me_when_user_has_null_email_then_returns_null(
    app: FastAPI,
    client: AsyncClient,
) -> None:
    """Edge case: usuario sin email retorna null en campo email."""
    profile = UserProfileOutputDTO(
        user_id="507f1f77bcf86cd799439011",
        phone="+573001234567",
        email=None,
        name=None,
        kyc_status="pending",
        mfa_enabled=False,
        created_at="2026-01-30T14:23:45.123Z",
    )
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = profile

    async def override_auth() -> str:
        return "507f1f77bcf86cd799439011"

    app.dependency_overrides[get_current_user] = override_auth
    try:
        with patch(
            "app.adapters.inbound.http.routers.users_router.get_user_profile_use_case",
            return_value=mock_uc,
        ):
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer valid.access.token"},
            )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] is None
    assert data["name"] is None


@pytest.mark.asyncio
async def test_users_me_state_kyc_approved_then_returns_approved(
    app: FastAPI,
    client: AsyncClient,
) -> None:
    """Estado: usuario con KYC approved retorna estado correcto."""
    profile = UserProfileOutputDTO(
        user_id="507f1f77bcf86cd799439011",
        phone="+573001234567",
        email="user@example.com",
        name="Juan",
        kyc_status="approved",
        mfa_enabled=False,
        created_at="2026-01-30T14:23:45.123Z",
    )
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = profile

    async def override_auth() -> str:
        return "507f1f77bcf86cd799439011"

    app.dependency_overrides[get_current_user] = override_auth
    try:
        with patch(
            "app.adapters.inbound.http.routers.users_router.get_user_profile_use_case",
            return_value=mock_uc,
        ):
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer valid.access.token"},
            )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    assert response.json()["kyc_status"] == "approved"


@pytest.mark.asyncio
async def test_users_me_state_mfa_enabled_then_returns_true(
    app: FastAPI,
    client: AsyncClient,
) -> None:
    """Estado: usuario con MFA habilitado retorna mfa_enabled true."""
    profile = UserProfileOutputDTO(
        user_id="507f1f77bcf86cd799439011",
        phone="+573001234567",
        email="user@example.com",
        name="Juan",
        kyc_status="approved",
        mfa_enabled=True,
        created_at="2026-01-30T14:23:45.123Z",
    )
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = profile

    async def override_auth() -> str:
        return "507f1f77bcf86cd799439011"

    app.dependency_overrides[get_current_user] = override_auth
    try:
        with patch(
            "app.adapters.inbound.http.routers.users_router.get_user_profile_use_case",
            return_value=mock_uc,
        ):
            response = await client.get(
                "/api/v1/users/me",
                headers={"Authorization": "Bearer valid.access.token"},
            )
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    assert response.json()["mfa_enabled"] is True


@pytest.mark.asyncio
async def test_users_me_concurrency_when_parallel_requests_then_all_succeed(
    app: FastAPI,
    client: AsyncClient,
) -> None:
    """Concurrencia: multiples peticiones simultaneas todas exitosas."""
    profile = UserProfileOutputDTO(
        user_id="507f1f77bcf86cd799439011",
        phone="+573001234567",
        email="user@example.com",
        name="Juan",
        kyc_status="approved",
        mfa_enabled=False,
        created_at="2026-01-30T14:23:45.123Z",
    )
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = profile

    async def override_auth() -> str:
        return "507f1f77bcf86cd799439011"

    app.dependency_overrides[get_current_user] = override_auth
    try:
        with patch(
            "app.adapters.inbound.http.routers.users_router.get_user_profile_use_case",
            return_value=mock_uc,
        ):
            tasks = [
                client.get(
                    "/api/v1/users/me",
                    headers={"Authorization": "Bearer valid.token"},
                )
                for _ in range(5)
            ]
            responses = await asyncio.gather(*tasks)
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    for resp in responses:
        assert resp.status_code == 200
        assert resp.json()["user_id"] == "507f1f77bcf86cd799439011"


@pytest.mark.asyncio
async def test_users_me_when_bearer_missing_prefix_then_returns_401(
    client: AsyncClient,
) -> None:
    """Edge case: Authorization header sin prefijo Bearer retorna 401."""
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Token some.token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Missing authorization token"
