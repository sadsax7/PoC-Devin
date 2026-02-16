"""Tests de integracion para el endpoint POST /auth/register.

Verifica el flujo completo del registro a traves del router HTTP,
incluyendo validacion, KYC mock y respuestas de error.
"""

from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

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
async def test_register_endpoint_when_valid_data_then_201(
    client: AsyncClient,
) -> None:
    """Caso positivo: registro exitoso retorna 201 con user_id."""
    # Arrange
    payload = {
        "phone": "+573001234567",
        "password": "ValidPass1!",
        "email": "test@example.com",
        "name": "Test User",
    }

    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_register_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = MagicMock(user_id="507f1f77bcf86cd799439011")
        mock_factory.return_value = mock_uc

        # Act
        response = await client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "507f1f77bcf86cd799439011"


@pytest.mark.asyncio
async def test_register_endpoint_when_duplicate_phone_then_409(
    client: AsyncClient,
) -> None:
    """Caso negativo: telefono duplicado retorna 409."""
    # Arrange
    from app.application.use_cases.register_user_use_case import DuplicatePhoneError

    payload = {
        "phone": "+573001234567",
        "password": "ValidPass1!",
    }

    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_register_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = DuplicatePhoneError("Phone number already registered")
        mock_factory.return_value = mock_uc

        # Act
        response = await client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "Phone number already registered"


@pytest.mark.asyncio
async def test_register_endpoint_when_kyc_rejected_then_400(
    client: AsyncClient,
) -> None:
    """Caso negativo: KYC rechazado retorna 400."""
    # Arrange
    from app.application.use_cases.register_user_use_case import KycRejectedError

    payload = {
        "phone": "+573001234500",
        "password": "ValidPass1!",
    }

    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_register_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = KycRejectedError(
            "KYC verification rejected for this phone number"
        )
        mock_factory.return_value = mock_uc

        # Act
        response = await client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 400
    assert "KYC verification rejected" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_endpoint_when_validation_error_then_422(
    client: AsyncClient,
) -> None:
    """Caso negativo: error de validacion retorna 422."""
    # Arrange
    from app.application.use_cases.register_user_use_case import ValidationError

    payload = {
        "phone": "+573001234567",
        "password": "weak",
    }

    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_register_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = ValidationError(
            field="password", message="Password must be at least 8 characters"
        )
        mock_factory.return_value = mock_uc

        # Act
        response = await client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["loc"] == ["body", "password"]
    assert detail[0]["type"] == "value_error"


@pytest.mark.asyncio
async def test_register_endpoint_when_invalid_phone_format_then_422(
    client: AsyncClient,
) -> None:
    """Caso negativo: telefono invalido retorna 422."""
    # Arrange
    payload = {
        "phone": "invalid",
        "password": "ValidPass1!",
    }

    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_register_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = ValueError(
            "Phone number 'invalid' does not match E.164 format"
        )
        mock_factory.return_value = mock_uc

        # Act
        response = await client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["loc"] == ["body", "phone"]


@pytest.mark.asyncio
async def test_register_endpoint_when_missing_phone_then_422(
    client: AsyncClient,
) -> None:
    """Edge case: payload sin phone retorna 422."""
    # Arrange
    payload = {
        "password": "ValidPass1!",
    }

    # Act
    response = await client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_endpoint_when_missing_password_then_422(
    client: AsyncClient,
) -> None:
    """Edge case: payload sin password retorna 422."""
    # Arrange
    payload = {
        "phone": "+573001234567",
    }

    # Act
    response = await client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_endpoint_when_only_required_fields_then_201(
    client: AsyncClient,
) -> None:
    """Caso positivo: solo campos obligatorios retorna 201."""
    # Arrange
    payload = {
        "phone": "+573001234567",
        "password": "ValidPass1!",
    }

    with patch(
        "app.adapters.inbound.http.routers.auth_router.get_register_user_use_case"
    ) as mock_factory:
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = MagicMock(user_id="abc123")
        mock_factory.return_value = mock_uc

        # Act
        response = await client.post("/api/v1/auth/register", json=payload)

    # Assert
    assert response.status_code == 201
    assert response.json()["user_id"] == "abc123"


@pytest.mark.asyncio
async def test_register_endpoint_when_empty_body_then_422(
    client: AsyncClient,
) -> None:
    """Edge case: body vacio retorna 422."""
    # Act
    response = await client.post("/api/v1/auth/register", json={})

    # Assert
    assert response.status_code == 422
