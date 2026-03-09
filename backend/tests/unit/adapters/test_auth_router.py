"""
Tests unitarios para POST /auth/register (sin DB).

Usa dependency overrides para inyectar mocks directamente.
Referencia: HU-BE-01 AC#7
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.adapters.inbound.http.dependencies.container import (
    get_register_user_use_case,
)
from app.application.use_cases.register_user import RegisterUserUseCase
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
