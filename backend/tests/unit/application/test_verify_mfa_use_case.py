"""Tests para el caso de uso de verificacion MFA."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.verify_mfa_dto import VerifyMfaInputDTO
from app.application.use_cases.verify_mfa_use_case import (
    InvalidMfaCodeError,
    MfaRateLimiter,
    TempTokenExpiredError,
    TooManyMfaAttemptsError,
    VerifyMfaUseCase,
)
from app.domain.entities.user import User
from app.domain.ports.token_provider_port import TokenProviderPort
from app.domain.ports.user_repository import UserRepositoryPort


def _make_use_case(
    repo: UserRepositoryPort,
    token: TokenProviderPort,
    rate_limiter: MfaRateLimiter,
) -> VerifyMfaUseCase:
    """Crea instancia del caso de uso con dependencias inyectadas.

    Args:
        repo: Repositorio de usuarios mock.
        token: Proveedor de tokens mock.
        rate_limiter: Limitador de intentos MFA.

    Returns:
        Instancia configurada de VerifyMfaUseCase.
    """
    return VerifyMfaUseCase(
        user_repository=repo,
        token_provider=token,
        rate_limiter=rate_limiter,
    )


@pytest.mark.asyncio
async def test_verify_mfa_when_correct_code_then_returns_tokens() -> None:
    """Caso positivo: codigo MFA correcto retorna tokens."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    rate_limiter = MfaRateLimiter()
    user = User(id="user123", phone="+573001234567", password_hash="h")
    mock_token.decode_token.return_value = {
        "sub": "user123",
        "type": "temp",
        "mfa_pending": True,
    }
    mock_repo.find_by_id.return_value = user
    mock_token.create_access_token.return_value = "access_tok"
    mock_token.create_refresh_token.return_value = "refresh_tok"
    use_case = _make_use_case(mock_repo, mock_token, rate_limiter)
    input_dto = VerifyMfaInputDTO(temp_token="valid.temp.token", code="123456")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.access_token == "access_tok"
    assert result.refresh_token == "refresh_tok"
    assert result.token_type == "Bearer"
    assert result.expires_in == 1800


@pytest.mark.asyncio
async def test_verify_mfa_when_wrong_code_then_raises_invalid_mfa_code() -> None:
    """Caso negativo: codigo MFA incorrecto."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    rate_limiter = MfaRateLimiter()
    mock_token.decode_token.return_value = {
        "sub": "user123",
        "type": "temp",
        "mfa_pending": True,
    }
    use_case = _make_use_case(mock_repo, mock_token, rate_limiter)
    input_dto = VerifyMfaInputDTO(temp_token="valid.temp.token", code="000000")

    # Act & Assert
    with pytest.raises(InvalidMfaCodeError) as exc_info:
        await use_case.execute(input_dto)
    assert exc_info.value.attempts_remaining == 2


@pytest.mark.asyncio
async def test_verify_mfa_when_expired_token_then_raises_expired() -> None:
    """Caso negativo: token temporal expirado."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    rate_limiter = MfaRateLimiter()
    mock_token.decode_token.side_effect = ValueError("Token has expired")
    use_case = _make_use_case(mock_repo, mock_token, rate_limiter)
    input_dto = VerifyMfaInputDTO(temp_token="expired.token", code="123456")

    # Act & Assert
    with pytest.raises(TempTokenExpiredError, match="Temporary token expired"):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_verify_mfa_when_token_not_temp_type_then_raises_expired() -> None:
    """Caso negativo: token no es de tipo temp."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    rate_limiter = MfaRateLimiter()
    mock_token.decode_token.return_value = {
        "sub": "user123",
        "type": "access",
        "mfa_pending": False,
    }
    use_case = _make_use_case(mock_repo, mock_token, rate_limiter)
    input_dto = VerifyMfaInputDTO(temp_token="access.token", code="123456")

    # Act & Assert
    with pytest.raises(TempTokenExpiredError):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_verify_mfa_when_three_failed_attempts_then_raises_too_many() -> None:
    """Caso de estado: 3 intentos fallidos bloquean verificacion."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    rate_limiter = MfaRateLimiter()
    mock_token.decode_token.return_value = {
        "sub": "user123",
        "type": "temp",
        "mfa_pending": True,
    }
    use_case = _make_use_case(mock_repo, mock_token, rate_limiter)
    bad_dto = VerifyMfaInputDTO(temp_token="valid.temp.token", code="000000")

    # Act - 3 intentos fallidos
    for _ in range(3):
        with pytest.raises(InvalidMfaCodeError):
            await use_case.execute(bad_dto)

    # Assert - 4to intento bloqueado
    with pytest.raises(TooManyMfaAttemptsError, match="Too many failed MFA attempts"):
        await use_case.execute(bad_dto)


@pytest.mark.asyncio
async def test_verify_mfa_when_success_after_failures_then_counter_resets() -> None:
    """Caso de estado: exito despues de fallos limpia el contador."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    rate_limiter = MfaRateLimiter()
    user = User(id="user123", phone="+573001234567", password_hash="h")
    mock_token.decode_token.return_value = {
        "sub": "user123",
        "type": "temp",
        "mfa_pending": True,
    }
    mock_repo.find_by_id.return_value = user
    mock_token.create_access_token.return_value = "access"
    mock_token.create_refresh_token.return_value = "refresh"
    use_case = _make_use_case(mock_repo, mock_token, rate_limiter)

    # Act - 2 fallos
    for _ in range(2):
        with pytest.raises(InvalidMfaCodeError):
            await use_case.execute(VerifyMfaInputDTO(temp_token="valid.temp.token", code="000000"))

    # Act - exito limpia contador
    result = await use_case.execute(VerifyMfaInputDTO(temp_token="valid.temp.token", code="123456"))
    assert result.access_token == "access"

    # Assert - puede fallar de nuevo sin bloqueo
    with pytest.raises(InvalidMfaCodeError) as exc_info:
        await use_case.execute(VerifyMfaInputDTO(temp_token="valid.temp.token", code="000000"))
    assert exc_info.value.attempts_remaining == 2


@pytest.mark.asyncio
async def test_verify_mfa_when_user_not_found_then_raises_expired() -> None:
    """Edge case: usuario no encontrado despues de decodificar token."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    rate_limiter = MfaRateLimiter()
    mock_token.decode_token.return_value = {
        "sub": "nonexistent",
        "type": "temp",
        "mfa_pending": True,
    }
    mock_repo.find_by_id.return_value = None
    use_case = _make_use_case(mock_repo, mock_token, rate_limiter)
    input_dto = VerifyMfaInputDTO(temp_token="valid.temp.token", code="123456")

    # Act & Assert
    with pytest.raises(TempTokenExpiredError):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_verify_mfa_when_token_missing_mfa_pending_then_raises_expired() -> None:
    """Edge case: token sin claim mfa_pending."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    rate_limiter = MfaRateLimiter()
    mock_token.decode_token.return_value = {
        "sub": "user123",
        "type": "temp",
    }
    use_case = _make_use_case(mock_repo, mock_token, rate_limiter)
    input_dto = VerifyMfaInputDTO(temp_token="valid.temp.token", code="123456")

    # Act & Assert
    with pytest.raises(TempTokenExpiredError):
        await use_case.execute(input_dto)
