"""
Tests unitarios para el router GET /users/me y la dependencia get_current_user.

Usa dependency overrides para inyectar mocks sin DB ni criptografía real.
Cubre autenticación (401), usuario no encontrado (404) y éxito (200).
Referencia: HU-BE-03 AC#1-3, agents.md §5.1.7.

Patrón: AAA (Arrange-Act-Assert).
Nomenclatura: test_<unit>_when_<condition>_then_<expected>.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.adapters.inbound.http.dependencies.container import (
    get_get_user_profile_use_case,
    get_token_provider,
)
from app.application.dtos.user_profile_dto import UserProfileOutputDTO
from app.application.use_cases.get_user_profile import (
    GetUserProfileUseCase,
    UserProfileNotFoundError,
)
from main import app

# ── Helpers ───────────────────────────────────────────────────

_USER_ID = "507f1f77bcf86cd799439011"
_VALID_CREATED_AT = "2026-01-30T14:23:45.000000Z"


def _make_profile_dto(
    *,
    user_id: str = _USER_ID,
    phone: str = "+573001234567",
    email: str | None = "alice@example.com",
    name: str | None = "Alice",
    kyc_status: str = "pending",
    mfa_enabled: bool = False,
    created_at: str = _VALID_CREATED_AT,
) -> UserProfileOutputDTO:
    """Construye un UserProfileOutputDTO para tests."""
    return UserProfileOutputDTO(
        user_id=user_id,
        phone=phone,
        email=email,
        name=name,
        kyc_status=kyc_status,
        mfa_enabled=mfa_enabled,
        created_at=created_at,
    )


def _mock_token_provider(
    *,
    should_raise: Exception | None = None,
    token_type: str = "access",
    sub: str = _USER_ID,
) -> MagicMock:
    """Crea un mock de TokenProviderPort."""
    provider = MagicMock()
    if should_raise:
        provider.verify_token = MagicMock(side_effect=should_raise)
    else:
        provider.verify_token = MagicMock(
            return_value={"sub": sub, "type": token_type, "phone": "+573001234567"}
        )
    return provider


def _mock_use_case(
    *,
    dto: UserProfileOutputDTO | None = None,
    should_raise: Exception | None = None,
) -> GetUserProfileUseCase:
    """Crea un mock del GetUserProfileUseCase."""
    uc = MagicMock()
    if should_raise:
        uc.execute = AsyncMock(side_effect=should_raise)
    else:
        uc.execute = AsyncMock(return_value=dto or _make_profile_dto())
    return uc


# ── 401 — Autenticación ────────────────────────────────────────


class TestUsersRouterUnauthorized:
    """Tests 401 del endpoint GET /users/me (sin DB)."""

    @pytest.mark.asyncio
    async def test_get_me_when_no_token_then_401_missing(self) -> None:
        """Sin header Authorization → 401 'Missing authorization token'."""
        # Arrange
        provider = _mock_token_provider()
        app.dependency_overrides[get_token_provider] = lambda: provider

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get("/users/me")

            # Assert
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Missing authorization token"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_when_expired_token_then_401_expired(self) -> None:
        """Token expirado → 401 'Token has expired'."""
        # Arrange
        provider = _mock_token_provider(should_raise=ValueError("Token has expired"))
        app.dependency_overrides[get_token_provider] = lambda: provider

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": "Bearer expired.token.here"},
                )

            # Assert
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Token has expired"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_when_invalid_signature_then_401_invalid(self) -> None:
        """Firma inválida → 401 'Invalid token signature'."""
        # Arrange
        provider = _mock_token_provider(
            should_raise=ValueError("Invalid token: signature verification failed")
        )
        app.dependency_overrides[get_token_provider] = lambda: provider

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": "Bearer bad.signature.token"},
                )

            # Assert
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Invalid token signature"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_when_refresh_token_then_401_wrong_type(self) -> None:
        """Refresh token → 401 'Invalid token type, access token required'."""
        # Arrange
        provider = _mock_token_provider(token_type="refresh")
        app.dependency_overrides[get_token_provider] = lambda: provider

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": "Bearer refresh.token.here"},
                )

            # Assert
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Invalid token type, access token required"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_when_temp_token_then_401_wrong_type(self) -> None:
        """Temp token (MFA) → 401 'Invalid token type, access token required'."""
        # Arrange
        provider = _mock_token_provider(token_type="temp")
        app.dependency_overrides[get_token_provider] = lambda: provider

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": "Bearer temp.token.here"},
                )

            # Assert
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Invalid token type, access token required"
        finally:
            app.dependency_overrides.clear()


# ── 404 — Usuario no encontrado ───────────────────────────────


class TestUsersRouterNotFound:
    """Tests 404 del endpoint GET /users/me."""

    @pytest.mark.asyncio
    async def test_get_me_when_user_deleted_then_404(self) -> None:
        """Usuario eliminado post-login → 404 'User not found'."""
        # Arrange
        provider = _mock_token_provider()
        uc = _mock_use_case(should_raise=UserProfileNotFoundError("not found"))
        app.dependency_overrides[get_token_provider] = lambda: provider
        app.dependency_overrides[get_get_user_profile_use_case] = lambda: uc

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": "Bearer valid.access.token"},
                )

            # Assert
            assert resp.status_code == 404
            assert resp.json()["detail"] == "User not found"
        finally:
            app.dependency_overrides.clear()


# ── 200 — Éxito ───────────────────────────────────────────────


class TestUsersRouterSuccess:
    """Tests 200 del endpoint GET /users/me."""

    @pytest.mark.asyncio
    async def test_get_me_when_valid_token_then_200_profile(self) -> None:
        """Token válido + usuario encontrado → 200 con datos del perfil."""
        # Arrange
        provider = _mock_token_provider()
        dto = _make_profile_dto()
        uc = _mock_use_case(dto=dto)
        app.dependency_overrides[get_token_provider] = lambda: provider
        app.dependency_overrides[get_get_user_profile_use_case] = lambda: uc

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": "Bearer valid.access.token"},
                )

            # Assert
            assert resp.status_code == 200
            body = resp.json()
            assert body["user_id"] == _USER_ID
            assert body["phone"] == "+573001234567"
            assert body["email"] == "alice@example.com"
            assert body["name"] == "Alice"
            assert body["kyc_status"] == "pending"
            assert body["mfa_enabled"] is False
            assert body["created_at"] == _VALID_CREATED_AT
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_when_valid_token_then_no_password_hash_in_response(
        self,
    ) -> None:
        """La respuesta 200 NUNCA incluye password_hash (AC#3 seguridad)."""
        # Arrange
        provider = _mock_token_provider()
        uc = _mock_use_case()
        app.dependency_overrides[get_token_provider] = lambda: provider
        app.dependency_overrides[get_get_user_profile_use_case] = lambda: uc

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": "Bearer valid.access.token"},
                )

            # Assert
            assert resp.status_code == 200
            assert "password_hash" not in resp.json()
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_when_user_has_null_fields_then_200_with_nulls(
        self,
    ) -> None:
        """Usuario sin email/name → 200 con email=null y name=null."""
        # Arrange
        provider = _mock_token_provider()
        dto = _make_profile_dto(email=None, name=None)
        uc = _mock_use_case(dto=dto)
        app.dependency_overrides[get_token_provider] = lambda: provider
        app.dependency_overrides[get_get_user_profile_use_case] = lambda: uc

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": "Bearer valid.access.token"},
                )

            # Assert
            assert resp.status_code == 200
            body = resp.json()
            assert body["email"] is None
            assert body["name"] is None
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_when_approved_kyc_then_kyc_status_approved(
        self,
    ) -> None:
        """Usuario con KYC approved → kyc_status es 'approved' en respuesta."""
        # Arrange
        provider = _mock_token_provider()
        dto = _make_profile_dto(kyc_status="approved")
        uc = _mock_use_case(dto=dto)
        app.dependency_overrides[get_token_provider] = lambda: provider
        app.dependency_overrides[get_get_user_profile_use_case] = lambda: uc

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": "Bearer valid.access.token"},
                )

            # Assert
            assert resp.status_code == 200
            assert resp.json()["kyc_status"] == "approved"
        finally:
            app.dependency_overrides.clear()
