"""Tests para el caso de uso de login de usuarios."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.login_user_dto import LoginUserInputDTO
from app.application.use_cases.login_user_use_case import (
    AccountLockedError,
    InvalidCredentialsError,
    LoginUserUseCase,
    UserNotFoundError,
)
from app.domain.entities.user import User
from app.domain.ports.password_hasher_port import PasswordHasherPort
from app.domain.ports.token_provider_port import TokenProviderPort
from app.domain.ports.user_repository import UserRepositoryPort


def _make_use_case(
    repo: UserRepositoryPort,
    hasher: PasswordHasherPort,
    token: TokenProviderPort,
) -> LoginUserUseCase:
    """Crea instancia del caso de uso con dependencias inyectadas.

    Args:
        repo: Repositorio de usuarios mock.
        hasher: Hasher de contrasenas mock.
        token: Proveedor de tokens mock.

    Returns:
        Instancia configurada de LoginUserUseCase.
    """
    return LoginUserUseCase(
        user_repository=repo,
        password_hasher=hasher,
        token_provider=token,
    )


def _make_user(
    user_id: str = "abc123",
    phone: str = "+573001234567",
    password_hash: str = "hashed_pw",
    kyc_status: str = "approved",
    mfa_enabled: bool = False,
) -> User:
    """Crea una entidad User para testing.

    Args:
        user_id: ID del usuario.
        phone: Telefono del usuario.
        password_hash: Hash de contrasena.
        kyc_status: Estado KYC.
        mfa_enabled: Si MFA esta habilitado.

    Returns:
        Entidad User configurada.
    """
    return User(
        id=user_id,
        phone=phone,
        password_hash=password_hash,
        kyc_status=kyc_status,
        mfa_enabled=mfa_enabled,
    )


@pytest.mark.asyncio
async def test_login_when_valid_credentials_no_mfa_then_returns_tokens() -> None:
    """Caso positivo: login exitoso sin MFA retorna access y refresh tokens."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_hasher = MagicMock(spec=PasswordHasherPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    user = _make_user()
    mock_repo.find_by_phone.return_value = user
    mock_hasher.verify_password.return_value = True
    mock_token.create_access_token.return_value = "access_tok"
    mock_token.create_refresh_token.return_value = "refresh_tok"
    use_case = _make_use_case(mock_repo, mock_hasher, mock_token)
    input_dto = LoginUserInputDTO(phone="+573001234567", password="Valid1234!")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.mfa_required is False
    assert result.access_token == "access_tok"
    assert result.refresh_token == "refresh_tok"
    assert result.token_type == "Bearer"
    assert result.expires_in == 1800


@pytest.mark.asyncio
async def test_login_when_valid_credentials_mfa_enabled_then_returns_temp_token() -> None:
    """Caso positivo: login con MFA retorna temp_token."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_hasher = MagicMock(spec=PasswordHasherPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    user = _make_user(mfa_enabled=True)
    mock_repo.find_by_phone.return_value = user
    mock_hasher.verify_password.return_value = True
    mock_token.create_temp_token.return_value = "temp_tok"
    use_case = _make_use_case(mock_repo, mock_hasher, mock_token)
    input_dto = LoginUserInputDTO(phone="+573001234567", password="Valid1234!")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.mfa_required is True
    assert result.temp_token == "temp_tok"
    assert result.message == "MFA verification required"


@pytest.mark.asyncio
async def test_login_when_phone_not_found_then_raises_user_not_found() -> None:
    """Caso negativo: telefono no registrado."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_hasher = MagicMock(spec=PasswordHasherPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    mock_repo.find_by_phone.return_value = None
    use_case = _make_use_case(mock_repo, mock_hasher, mock_token)
    input_dto = LoginUserInputDTO(phone="+573001234567", password="Valid1234!")

    # Act & Assert
    with pytest.raises(UserNotFoundError, match="Phone number not registered"):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_login_when_wrong_password_then_raises_invalid_credentials() -> None:
    """Caso negativo: contrasena incorrecta."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_hasher = MagicMock(spec=PasswordHasherPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    user = _make_user()
    mock_repo.find_by_phone.return_value = user
    mock_hasher.verify_password.return_value = False
    use_case = _make_use_case(mock_repo, mock_hasher, mock_token)
    input_dto = LoginUserInputDTO(phone="+573001234567", password="WrongPass1!")

    # Act & Assert
    with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_login_when_account_locked_then_raises_account_locked() -> None:
    """Caso negativo: cuenta bloqueada por KYC rejected."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_hasher = MagicMock(spec=PasswordHasherPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    user = _make_user(kyc_status="rejected")
    mock_repo.find_by_phone.return_value = user
    use_case = _make_use_case(mock_repo, mock_hasher, mock_token)
    input_dto = LoginUserInputDTO(phone="+573001234567", password="Valid1234!")

    # Act & Assert
    with pytest.raises(AccountLockedError, match="Account locked"):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_login_when_password_too_short_then_raises_invalid_credentials() -> None:
    """Edge case: contrasena por debajo del minimo."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_hasher = MagicMock(spec=PasswordHasherPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    use_case = _make_use_case(mock_repo, mock_hasher, mock_token)
    input_dto = LoginUserInputDTO(phone="+573001234567", password="short")

    # Act & Assert
    with pytest.raises(InvalidCredentialsError):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_login_when_password_exactly_min_length_then_proceeds() -> None:
    """Edge case: contrasena exactamente en el minimo (8 chars)."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_hasher = MagicMock(spec=PasswordHasherPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    user = _make_user()
    mock_repo.find_by_phone.return_value = user
    mock_hasher.verify_password.return_value = True
    mock_token.create_access_token.return_value = "tok"
    mock_token.create_refresh_token.return_value = "ref"
    use_case = _make_use_case(mock_repo, mock_hasher, mock_token)
    input_dto = LoginUserInputDTO(phone="+573001234567", password="12345678")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.mfa_required is False


@pytest.mark.asyncio
async def test_login_when_kyc_pending_and_valid_creds_then_login_succeeds() -> None:
    """Caso de estado: usuario con KYC pendiente puede hacer login."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_hasher = MagicMock(spec=PasswordHasherPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    user = _make_user(kyc_status="pending")
    mock_repo.find_by_phone.return_value = user
    mock_hasher.verify_password.return_value = True
    mock_token.create_access_token.return_value = "tok"
    mock_token.create_refresh_token.return_value = "ref"
    use_case = _make_use_case(mock_repo, mock_hasher, mock_token)
    input_dto = LoginUserInputDTO(phone="+573001234567", password="Valid1234!")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.mfa_required is False
    assert result.access_token == "tok"


@pytest.mark.asyncio
async def test_login_when_user_id_none_then_raises_runtime_error() -> None:
    """Edge case: usuario sin ID asignado."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_hasher = MagicMock(spec=PasswordHasherPort)
    mock_token = MagicMock(spec=TokenProviderPort)
    user = _make_user()
    user.id = None
    mock_repo.find_by_phone.return_value = user
    mock_hasher.verify_password.return_value = True
    use_case = _make_use_case(mock_repo, mock_hasher, mock_token)
    input_dto = LoginUserInputDTO(phone="+573001234567", password="Valid1234!")

    # Act & Assert
    with pytest.raises(RuntimeError, match="User ID is missing"):
        await use_case.execute(input_dto)
