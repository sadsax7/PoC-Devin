"""
Tests de integración HTTP para GET /users/me.

Usa httpx.AsyncClient contra la app FastAPI con dependency_overrides
para verificar el contrato HTTP completo del endpoint de perfil.
Referencia: HU-BE-03 AC#1-4, agents.md §5.1.7.

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

# ── Constantes ────────────────────────────────────────────────

_USER_ID = "507f1f77bcf86cd799439011"
_CREATED_AT = "2026-01-30T14:23:45.000000Z"
_BEARER_TOKEN = "eyJhbGciOiJSUzI1NiJ9.test.token"


# ── Helpers ───────────────────────────────────────────────────


def _make_token_provider(
    *,
    raises: Exception | None = None,
    token_type: str = "access",
    sub: str = _USER_ID,
) -> MagicMock:
    """Crea mock de TokenProviderPort."""
    tp = MagicMock()
    if raises:
        tp.verify_token = MagicMock(side_effect=raises)
    else:
        tp.verify_token = MagicMock(
            return_value={"sub": sub, "type": token_type, "phone": "+573001234567"}
        )
    return tp


def _make_use_case(
    *,
    dto: UserProfileOutputDTO | None = None,
    raises: Exception | None = None,
) -> GetUserProfileUseCase:
    """Crea mock de GetUserProfileUseCase."""
    uc = MagicMock(spec=GetUserProfileUseCase)
    if raises:
        uc.execute = AsyncMock(side_effect=raises)
    else:
        resolved_dto = dto or UserProfileOutputDTO(
            user_id=_USER_ID,
            phone="+573001234567",
            email="alice@example.com",
            name="Alice",
            kyc_status="pending",
            mfa_enabled=False,
            created_at=_CREATED_AT,
        )
        uc.execute = AsyncMock(return_value=resolved_dto)
    return uc


# ── Contrato HTTP — autenticación ─────────────────────────────


class TestGetMeAuthContract:
    """Tests del contrato HTTP de autenticación para GET /users/me."""

    @pytest.mark.asyncio
    async def test_get_me_contract_when_no_authorization_header_then_401(
        self,
    ) -> None:
        """Sin header Authorization → 401 con mensaje específico."""
        # Arrange
        tp = _make_token_provider()
        app.dependency_overrides[get_token_provider] = lambda: tp

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
    async def test_get_me_contract_when_token_expired_then_401(self) -> None:
        """Token expirado → 401 con mensaje de expiración."""
        # Arrange
        tp = _make_token_provider(raises=ValueError("Token has expired"))
        app.dependency_overrides[get_token_provider] = lambda: tp

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": f"Bearer {_BEARER_TOKEN}"},
                )

            # Assert
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Token has expired"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_contract_when_invalid_token_then_401(self) -> None:
        """Token con firma inválida → 401 con mensaje de firma inválida."""
        # Arrange
        tp = _make_token_provider(raises=ValueError("Invalid token: signature mismatch"))
        app.dependency_overrides[get_token_provider] = lambda: tp

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": f"Bearer {_BEARER_TOKEN}"},
                )

            # Assert
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Invalid token signature"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_contract_when_refresh_token_then_401_wrong_type(
        self,
    ) -> None:
        """Refresh token → 401 indicando tipo de token incorrecto."""
        # Arrange
        tp = _make_token_provider(token_type="refresh")
        app.dependency_overrides[get_token_provider] = lambda: tp

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": f"Bearer {_BEARER_TOKEN}"},
                )

            # Assert
            assert resp.status_code == 401
            assert resp.json()["detail"] == "Invalid token type, access token required"
        finally:
            app.dependency_overrides.clear()


# ── Contrato HTTP — recurso ───────────────────────────────────


class TestGetMeResourceContract:
    """Tests del contrato HTTP de acceso al recurso GET /users/me."""

    @pytest.mark.asyncio
    async def test_get_me_contract_when_user_not_found_then_404(self) -> None:
        """Usuario eliminado post-login → 404 con mensaje descriptivo."""
        # Arrange
        tp = _make_token_provider()
        uc = _make_use_case(raises=UserProfileNotFoundError("gone"))
        app.dependency_overrides[get_token_provider] = lambda: tp
        app.dependency_overrides[get_get_user_profile_use_case] = lambda: uc

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": f"Bearer {_BEARER_TOKEN}"},
                )

            # Assert
            assert resp.status_code == 404
            assert resp.json()["detail"] == "User not found"
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_contract_when_valid_token_then_200_full_profile(
        self,
    ) -> None:
        """Token válido + usuario activo → 200 con perfil completo (AC#3)."""
        # Arrange
        tp = _make_token_provider()
        uc = _make_use_case()
        app.dependency_overrides[get_token_provider] = lambda: tp
        app.dependency_overrides[get_get_user_profile_use_case] = lambda: uc

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": f"Bearer {_BEARER_TOKEN}"},
                )

            # Assert
            assert resp.status_code == 200
            body = resp.json()

            # Campos incluidos (AC#3)
            assert body["user_id"] == _USER_ID
            assert body["phone"] == "+573001234567"
            assert body["email"] == "alice@example.com"
            assert body["name"] == "Alice"
            assert body["kyc_status"] == "pending"
            assert body["mfa_enabled"] is False
            assert body["created_at"] == _CREATED_AT

            # Campos excluidos (AC#3 — seguridad)
            assert "password_hash" not in body
            assert "mfa_secret" not in body
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_contract_when_user_no_email_then_email_null(
        self,
    ) -> None:
        """Usuario sin email → campo email es null en la respuesta JSON."""
        # Arrange
        tp = _make_token_provider()
        dto = UserProfileOutputDTO(
            user_id=_USER_ID,
            phone="+573001234567",
            email=None,
            name=None,
            kyc_status="approved",
            mfa_enabled=True,
            created_at=_CREATED_AT,
        )
        uc = _make_use_case(dto=dto)
        app.dependency_overrides[get_token_provider] = lambda: tp
        app.dependency_overrides[get_get_user_profile_use_case] = lambda: uc

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": f"Bearer {_BEARER_TOKEN}"},
                )

            # Assert
            assert resp.status_code == 200
            body = resp.json()
            assert body["email"] is None
            assert body["name"] is None
            assert body["kyc_status"] == "approved"
            assert body["mfa_enabled"] is True
        finally:
            app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_get_me_contract_response_includes_created_at_iso8601(
        self,
    ) -> None:
        """Respuesta 200 incluye created_at en formato ISO 8601 con Z."""
        # Arrange
        tp = _make_token_provider()
        uc = _make_use_case()
        app.dependency_overrides[get_token_provider] = lambda: tp
        app.dependency_overrides[get_get_user_profile_use_case] = lambda: uc

        try:
            # Act
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                resp = await ac.get(
                    "/users/me",
                    headers={"Authorization": f"Bearer {_BEARER_TOKEN}"},
                )

            # Assert
            assert resp.status_code == 200
            created_at = resp.json()["created_at"]
            assert "T" in created_at
            assert created_at.endswith("Z")
        finally:
            app.dependency_overrides.clear()
