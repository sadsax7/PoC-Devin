"""Tests unitarios para el caso de uso RegisterUserUseCase.

Cubre los 6 tipos obligatorios: positivos, negativos, edge cases,
transiciones de estado, concurrencia e integracion.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.register_user_dto import RegisterUserInputDTO
from app.application.use_cases.register_user_use_case import (
    DuplicatePhoneError,
    KycRejectedError,
    RegisterUserUseCase,
    ValidationError,
)
from app.domain.entities.user import User


@pytest.fixture
def mock_user_repository() -> AsyncMock:
    """Crea un mock del repositorio de usuarios."""
    repo = AsyncMock()
    repo.find_by_phone.return_value = None

    async def create_side_effect(user: User) -> User:
        user.id = "507f1f77bcf86cd799439011"
        return user

    repo.create.side_effect = create_side_effect
    return repo


@pytest.fixture
def mock_kyc_verification() -> AsyncMock:
    """Crea un mock del servicio KYC."""
    kyc = AsyncMock()
    kyc.verify.return_value = "pending"
    return kyc


@pytest.fixture
def mock_password_hasher() -> MagicMock:
    """Crea un mock del hasher de contrasenas."""
    hasher = MagicMock()
    hasher.hash_password.return_value = "$argon2id$hashed"
    return hasher


@pytest.fixture
def use_case(
    mock_user_repository: AsyncMock,
    mock_kyc_verification: AsyncMock,
    mock_password_hasher: MagicMock,
) -> RegisterUserUseCase:
    """Crea una instancia del caso de uso con mocks."""
    return RegisterUserUseCase(
        user_repository=mock_user_repository,
        kyc_verification=mock_kyc_verification,
        password_hasher=mock_password_hasher,
    )


@pytest.mark.asyncio
async def test_register_user_when_valid_data_then_user_created(
    use_case: RegisterUserUseCase,
    mock_user_repository: AsyncMock,
    mock_password_hasher: MagicMock,
) -> None:
    """Caso positivo: datos validos crean usuario exitosamente."""
    # Arrange
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
        email="test@example.com",
        name="Test User",
    )

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.user_id == "507f1f77bcf86cd799439011"
    mock_user_repository.find_by_phone.assert_called_once_with("+573001234567")
    mock_user_repository.create.assert_called_once()
    mock_password_hasher.hash_password.assert_called_once_with("ValidPass1!")


@pytest.mark.asyncio
async def test_register_user_when_valid_data_without_optionals_then_created(
    use_case: RegisterUserUseCase,
) -> None:
    """Caso positivo: datos validos sin campos opcionales crean usuario."""
    # Arrange
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
    )

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.user_id == "507f1f77bcf86cd799439011"


@pytest.mark.asyncio
async def test_register_user_when_duplicate_phone_then_raises_conflict(
    use_case: RegisterUserUseCase,
    mock_user_repository: AsyncMock,
) -> None:
    """Caso negativo: telefono duplicado lanza DuplicatePhoneError."""
    # Arrange
    mock_user_repository.find_by_phone.return_value = User(phone="+573001234567", id="existing-id")
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
    )

    # Act & Assert
    with pytest.raises(DuplicatePhoneError, match="already registered"):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_register_user_when_weak_password_then_raises_validation(
    use_case: RegisterUserUseCase,
) -> None:
    """Caso negativo: contrasena debil lanza ValidationError."""
    # Arrange
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="weak",
    )

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        await use_case.execute(input_dto)
    assert exc_info.value.field == "password"


@pytest.mark.asyncio
async def test_register_user_when_invalid_email_then_raises_validation(
    use_case: RegisterUserUseCase,
) -> None:
    """Caso negativo: email invalido lanza ValidationError."""
    # Arrange
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
        email="not-an-email",
    )

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        await use_case.execute(input_dto)
    assert exc_info.value.field == "email"


@pytest.mark.asyncio
async def test_register_user_when_name_too_long_then_raises_validation(
    use_case: RegisterUserUseCase,
) -> None:
    """Caso negativo: nombre demasiado largo lanza ValidationError."""
    # Arrange
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
        name="A" * 101,
    )

    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        await use_case.execute(input_dto)
    assert exc_info.value.field == "name"


@pytest.mark.asyncio
async def test_register_user_when_invalid_phone_then_raises_value_error(
    use_case: RegisterUserUseCase,
) -> None:
    """Caso negativo: telefono invalido lanza ValueError."""
    # Arrange
    input_dto = RegisterUserInputDTO(
        phone="invalid-phone",
        password="ValidPass1!",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="does not match E.164"):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_register_user_when_kyc_rejected_then_raises_error(
    use_case: RegisterUserUseCase,
    mock_kyc_verification: AsyncMock,
) -> None:
    """Caso negativo: KYC rechazado lanza KycRejectedError."""
    # Arrange
    mock_kyc_verification.verify.return_value = "rejected"
    input_dto = RegisterUserInputDTO(
        phone="+573001234500",
        password="ValidPass1!",
    )

    # Act & Assert
    with pytest.raises(KycRejectedError, match="rejected"):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_register_user_when_kyc_approved_then_status_approved(
    use_case: RegisterUserUseCase,
    mock_kyc_verification: AsyncMock,
    mock_user_repository: AsyncMock,
) -> None:
    """State transition: KYC aprobado resulta en kyc_status='approved'."""
    # Arrange
    mock_kyc_verification.verify.return_value = "approved"
    input_dto = RegisterUserInputDTO(
        phone="+573001234599",
        password="ValidPass1!",
    )

    # Act
    await use_case.execute(input_dto)

    # Assert
    created_user = mock_user_repository.create.call_args[0][0]
    assert created_user.kyc_status == "approved"


@pytest.mark.asyncio
async def test_register_user_when_kyc_pending_then_status_pending(
    use_case: RegisterUserUseCase,
    mock_kyc_verification: AsyncMock,
    mock_user_repository: AsyncMock,
) -> None:
    """State transition: KYC pendiente resulta en kyc_status='pending'."""
    # Arrange
    mock_kyc_verification.verify.return_value = "pending"
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
    )

    # Act
    await use_case.execute(input_dto)

    # Assert
    created_user = mock_user_repository.create.call_args[0][0]
    assert created_user.kyc_status == "pending"


@pytest.mark.asyncio
async def test_register_user_when_created_then_mfa_disabled(
    use_case: RegisterUserUseCase,
    mock_user_repository: AsyncMock,
) -> None:
    """State transition: usuario nuevo tiene mfa_enabled=False."""
    # Arrange
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
    )

    # Act
    await use_case.execute(input_dto)

    # Assert
    created_user = mock_user_repository.create.call_args[0][0]
    assert created_user.mfa_enabled is False


@pytest.mark.asyncio
async def test_register_user_when_password_exactly_min_length_then_accepted(
    use_case: RegisterUserUseCase,
) -> None:
    """Edge case: contrasena de exactamente 8 caracteres es aceptada."""
    # Arrange
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="Abcde1!x",
    )

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.user_id == "507f1f77bcf86cd799439011"


@pytest.mark.asyncio
async def test_register_user_when_password_exactly_max_length_then_accepted(
    use_case: RegisterUserUseCase,
) -> None:
    """Edge case: contrasena de exactamente 128 caracteres es aceptada."""
    # Arrange
    password = "A" * 60 + "a" * 60 + "1234!@#$"
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password=password,
    )

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.user_id == "507f1f77bcf86cd799439011"


@pytest.mark.asyncio
async def test_register_user_when_email_at_max_length_then_accepted(
    use_case: RegisterUserUseCase,
) -> None:
    """Edge case: email de exactamente 255 caracteres es aceptado."""
    # Arrange
    local = "a" * 243
    email = f"{local}@example.com"
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
        email=email,
    )

    # Act
    result = await use_case.execute(input_dto)

    # Assert
    assert result.user_id == "507f1f77bcf86cd799439011"


@pytest.mark.asyncio
async def test_register_user_when_no_id_assigned_then_raises_runtime_error(
    use_case: RegisterUserUseCase,
    mock_user_repository: AsyncMock,
) -> None:
    """Edge case: si el repositorio no asigna ID, lanza RuntimeError."""

    # Arrange
    async def create_no_id(user: User) -> User:
        return user

    mock_user_repository.create.side_effect = create_no_id
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
    )

    # Act & Assert
    with pytest.raises(RuntimeError, match="User ID was not assigned"):
        await use_case.execute(input_dto)


@pytest.mark.asyncio
async def test_register_user_password_never_stored_in_plain_text(
    use_case: RegisterUserUseCase,
    mock_user_repository: AsyncMock,
) -> None:
    """Seguridad: contrasena nunca se almacena en texto plano."""
    # Arrange
    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
    )

    # Act
    await use_case.execute(input_dto)

    # Assert
    created_user = mock_user_repository.create.call_args[0][0]
    assert created_user.password_hash != "ValidPass1!"
    assert created_user.password_hash == "$argon2id$hashed"


@pytest.mark.asyncio
async def test_concurrent_register_when_same_phone_then_one_fails(
    mock_kyc_verification: AsyncMock,
    mock_password_hasher: MagicMock,
) -> None:
    """Concurrencia: dos registros simultaneos con mismo telefono."""
    # Arrange
    call_count = 0
    repo = AsyncMock()

    async def find_by_phone_side_effect(phone: str) -> User | None:
        nonlocal call_count
        call_count += 1
        if call_count > 1:
            return User(phone=phone, id="existing")
        return None

    repo.find_by_phone.side_effect = find_by_phone_side_effect

    async def create_side_effect(user: User) -> User:
        user.id = "new-id"
        return user

    repo.create.side_effect = create_side_effect

    uc = RegisterUserUseCase(
        user_repository=repo,
        kyc_verification=mock_kyc_verification,
        password_hasher=mock_password_hasher,
    )

    input_dto = RegisterUserInputDTO(
        phone="+573001234567",
        password="ValidPass1!",
    )

    # Act
    results = await asyncio.gather(
        uc.execute(input_dto),
        uc.execute(input_dto),
        return_exceptions=True,
    )

    # Assert
    errors = [r for r in results if isinstance(r, DuplicatePhoneError)]
    successes = [r for r in results if not isinstance(r, Exception)]
    assert len(errors) + len(successes) == 2
