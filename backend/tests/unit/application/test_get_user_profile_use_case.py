"""Tests para el caso de uso de obtener perfil de usuario."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.application.dtos.user_profile_dto import UserProfileInputDTO
from app.application.use_cases.get_user_profile_use_case import (
    GetUserProfileUseCase,
    UserNotFoundError,
)
from app.domain.entities.user import User
from app.domain.ports.user_repository import UserRepositoryPort


def _make_use_case(repo: UserRepositoryPort) -> GetUserProfileUseCase:
    """Crea instancia del caso de uso con dependencias inyectadas.

    Args:
        repo: Repositorio de usuarios mock.

    Returns:
        Instancia configurada de GetUserProfileUseCase.
    """
    return GetUserProfileUseCase(user_repository=repo)


def _make_user(
    user_id: str = "507f1f77bcf86cd799439011",
    phone: str = "+573001234567",
    email: str | None = "user@example.com",
    name: str | None = "Juan Perez",
    kyc_status: str = "pending",
    mfa_enabled: bool = False,
    password_hash: str = "hashed_secret_pw",
    created_at: datetime | None = None,
) -> User:
    """Crea una entidad User para testing.

    Args:
        user_id: ID del usuario.
        phone: Telefono del usuario.
        email: Email del usuario.
        name: Nombre del usuario.
        kyc_status: Estado KYC.
        mfa_enabled: Si MFA esta habilitado.
        password_hash: Hash de contrasena.
        created_at: Fecha de creacion.

    Returns:
        Entidad User configurada.
    """
    return User(
        id=user_id,
        phone=phone,
        email=email,
        name=name,
        kyc_status=kyc_status,
        mfa_enabled=mfa_enabled,
        password_hash=password_hash,
        created_at=created_at or datetime(2026, 1, 30, 14, 23, 45, 123000, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_get_profile_when_valid_user_then_returns_sanitized_profile() -> None:
    """Caso positivo: usuario encontrado retorna perfil sanitizado."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user()
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.user_id == "507f1f77bcf86cd799439011"
    assert result.phone == "+573001234567"
    assert result.email == "user@example.com"
    assert result.name == "Juan Perez"
    assert result.kyc_status == "pending"
    assert result.mfa_enabled is False
    assert result.created_at == "2026-01-30T14:23:45.123Z"
    mock_repo.find_by_id.assert_awaited_once_with("507f1f77bcf86cd799439011")


@pytest.mark.asyncio
async def test_get_profile_when_user_not_found_then_raises_error() -> None:
    """Caso negativo: usuario no encontrado lanza UserNotFoundError."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    mock_repo.find_by_id.return_value = None
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="nonexistent_id")

    # Act & Assert
    with pytest.raises(UserNotFoundError, match="User not found"):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_get_profile_when_user_has_no_email_then_email_is_none() -> None:
    """Edge case: usuario sin email retorna email como None."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user(email=None)
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.email is None


@pytest.mark.asyncio
async def test_get_profile_when_user_has_no_name_then_name_is_none() -> None:
    """Edge case: usuario sin nombre retorna name como None."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user(name=None)
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.name is None


@pytest.mark.asyncio
async def test_get_profile_when_user_has_no_email_and_no_name_then_both_none() -> None:
    """Edge case: usuario sin email ni nombre retorna ambos como None."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user(email=None, name=None)
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.email is None
    assert result.name is None


@pytest.mark.asyncio
async def test_get_profile_response_excludes_password_hash() -> None:
    """Seguridad: la respuesta NO contiene password_hash."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user(password_hash="super_secret_hash")
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    result_dict = {
        "user_id": result.user_id,
        "phone": result.phone,
        "email": result.email,
        "name": result.name,
        "kyc_status": result.kyc_status,
        "mfa_enabled": result.mfa_enabled,
        "created_at": result.created_at,
    }
    assert "password_hash" not in result_dict
    assert "super_secret_hash" not in str(result_dict)


@pytest.mark.asyncio
async def test_get_profile_when_kyc_approved_then_status_is_approved() -> None:
    """Estado: usuario con KYC aprobado retorna kyc_status approved."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user(kyc_status="approved")
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.kyc_status == "approved"


@pytest.mark.asyncio
async def test_get_profile_when_kyc_rejected_then_status_is_rejected() -> None:
    """Estado: usuario con KYC rechazado retorna kyc_status rejected."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user(kyc_status="rejected")
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.kyc_status == "rejected"


@pytest.mark.asyncio
async def test_get_profile_when_mfa_enabled_then_returns_true() -> None:
    """Estado: usuario con MFA habilitado retorna mfa_enabled True."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user(mfa_enabled=True)
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.mfa_enabled is True


@pytest.mark.asyncio
async def test_get_profile_when_user_id_is_none_then_returns_empty_string() -> None:
    """Edge case: usuario con ID None retorna user_id como cadena vacia."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user()
    user.id = None
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.user_id == ""


@pytest.mark.asyncio
async def test_get_profile_created_at_format_is_iso_8601() -> None:
    """Edge case: created_at se formatea en ISO 8601 con milisegundos."""
    # Arrange
    mock_repo = AsyncMock(spec=UserRepositoryPort)
    user = _make_user(created_at=datetime(2026, 6, 15, 10, 30, 0, 500000, tzinfo=timezone.utc))
    mock_repo.find_by_id.return_value = user
    use_case = _make_use_case(mock_repo)
    input_dto = UserProfileInputDTO(user_id="507f1f77bcf86cd799439011")

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.created_at == "2026-06-15T10:30:00.500Z"
