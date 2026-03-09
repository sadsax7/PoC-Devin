"""
Tests de integración para POST /auth/register (endpoint HTTP).

Usa httpx.AsyncClient contra la app FastAPI con dependency_overrides.
Referencia: HU-BE-01 AC#7, DoD#10
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.adapters.inbound.http.dependencies.container import get_register_user_use_case
from app.application.use_cases.register_user import RegisterUserUseCase
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
