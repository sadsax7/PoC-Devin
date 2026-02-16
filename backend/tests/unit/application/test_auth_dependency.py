"""Tests para la dependencia de autenticacion JWT (get_current_user)."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.adapters.inbound.http.dependencies.auth import get_current_user


def _make_request(auth_header: str | None = None) -> MagicMock:
    """Crea un mock de Request con el header Authorization.

    Args:
        auth_header: Valor del header Authorization.

    Returns:
        Mock de Request configurado.
    """
    request = MagicMock()
    request.headers = MagicMock()
    request.headers.get = MagicMock(return_value=auth_header)
    return request


@pytest.mark.asyncio
async def test_get_current_user_when_valid_access_token_then_returns_user_id() -> None:
    """Caso positivo: token de acceso valido retorna user_id."""
    # Arrange
    request = _make_request("Bearer valid.access.token")
    mock_provider = MagicMock()
    mock_provider.decode_token.return_value = {
        "sub": "507f1f77bcf86cd799439011",
        "type": "access",
    }

    # Act
    with patch(
        "app.adapters.inbound.http.dependencies.auth._get_token_provider",
        return_value=mock_provider,
    ):
        result = await get_current_user(request)

    # Assert
    assert result == "507f1f77bcf86cd799439011"


@pytest.mark.asyncio
async def test_get_current_user_when_no_auth_header_then_raises_401() -> None:
    """Caso negativo: sin header Authorization retorna 401."""
    # Arrange
    request = _make_request(None)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Missing authorization token"


@pytest.mark.asyncio
async def test_get_current_user_when_empty_auth_header_then_raises_401() -> None:
    """Caso negativo: header Authorization vacio retorna 401."""
    # Arrange
    request = _make_request("")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Missing authorization token"


@pytest.mark.asyncio
async def test_get_current_user_when_invalid_token_then_raises_401() -> None:
    """Caso negativo: token invalido retorna 401."""
    # Arrange
    request = _make_request("Bearer invalid.token")
    mock_provider = MagicMock()
    mock_provider.decode_token.side_effect = ValueError("Invalid token: bad signature")

    # Act & Assert
    with patch(
        "app.adapters.inbound.http.dependencies.auth._get_token_provider",
        return_value=mock_provider,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token signature"


@pytest.mark.asyncio
async def test_get_current_user_when_expired_token_then_raises_401() -> None:
    """Caso negativo: token expirado retorna 401."""
    # Arrange
    request = _make_request("Bearer expired.token")
    mock_provider = MagicMock()
    mock_provider.decode_token.side_effect = ValueError("Token has expired")

    # Act & Assert
    with patch(
        "app.adapters.inbound.http.dependencies.auth._get_token_provider",
        return_value=mock_provider,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token has expired"


@pytest.mark.asyncio
async def test_get_current_user_when_refresh_token_then_raises_401() -> None:
    """Caso negativo: token tipo refresh rechazado."""
    # Arrange
    request = _make_request("Bearer refresh.token")
    mock_provider = MagicMock()
    mock_provider.decode_token.return_value = {
        "sub": "507f1f77bcf86cd799439011",
        "type": "refresh",
    }

    # Act & Assert
    with patch(
        "app.adapters.inbound.http.dependencies.auth._get_token_provider",
        return_value=mock_provider,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token type, access token required"


@pytest.mark.asyncio
async def test_get_current_user_when_temp_token_then_raises_401() -> None:
    """Caso negativo: token tipo temp rechazado."""
    # Arrange
    request = _make_request("Bearer temp.token")
    mock_provider = MagicMock()
    mock_provider.decode_token.return_value = {
        "sub": "507f1f77bcf86cd799439011",
        "type": "temp",
    }

    # Act & Assert
    with patch(
        "app.adapters.inbound.http.dependencies.auth._get_token_provider",
        return_value=mock_provider,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token type, access token required"


@pytest.mark.asyncio
async def test_get_current_user_when_no_bearer_prefix_then_raises_401() -> None:
    """Edge case: header sin prefijo Bearer retorna 401."""
    # Arrange
    request = _make_request("Token some.token.here")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Missing authorization token"


@pytest.mark.asyncio
async def test_get_current_user_when_bearer_only_no_token_then_raises_401() -> None:
    """Edge case: header con Bearer pero sin token retorna 401."""
    # Arrange
    request = _make_request("Bearer ")

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Missing authorization token"


@pytest.mark.asyncio
async def test_get_current_user_when_sub_missing_then_raises_401() -> None:
    """Edge case: token sin claim sub retorna 401."""
    # Arrange
    request = _make_request("Bearer valid.token")
    mock_provider = MagicMock()
    mock_provider.decode_token.return_value = {"type": "access"}

    # Act & Assert
    with patch(
        "app.adapters.inbound.http.dependencies.auth._get_token_provider",
        return_value=mock_provider,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token signature"


@pytest.mark.asyncio
async def test_get_current_user_when_sub_empty_string_then_raises_401() -> None:
    """Edge case: token con sub vacio retorna 401."""
    # Arrange
    request = _make_request("Bearer valid.token")
    mock_provider = MagicMock()
    mock_provider.decode_token.return_value = {"sub": "", "type": "access"}

    # Act & Assert
    with patch(
        "app.adapters.inbound.http.dependencies.auth._get_token_provider",
        return_value=mock_provider,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token signature"


@pytest.mark.asyncio
async def test_get_current_user_when_no_type_claim_then_raises_401() -> None:
    """Edge case: token sin claim type retorna 401."""
    # Arrange
    request = _make_request("Bearer valid.token")
    mock_provider = MagicMock()
    mock_provider.decode_token.return_value = {"sub": "user123"}

    # Act & Assert
    with patch(
        "app.adapters.inbound.http.dependencies.auth._get_token_provider",
        return_value=mock_provider,
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token type, access token required"
