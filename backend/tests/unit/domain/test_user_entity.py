"""Tests unitarios para la entidad User del dominio."""

from datetime import datetime, timezone

from app.domain.entities.user import User


def test_user_when_created_with_phone_then_has_correct_attributes() -> None:
    """Caso positivo: User con phone tiene atributos correctos."""
    # Arrange & Act
    user = User(phone="+573001234567")

    # Assert
    assert user.phone == "+573001234567"
    assert user.password_hash == ""
    assert user.email is None
    assert user.name is None
    assert user.kyc_status == "pending"
    assert user.mfa_enabled is False
    assert user.id is None
    assert isinstance(user.created_at, datetime)


def test_user_when_created_with_all_fields_then_has_correct_attributes() -> None:
    """Caso positivo: User con todos los campos tiene atributos correctos."""
    # Arrange
    now = datetime.now(timezone.utc)

    # Act
    user = User(
        phone="+573001234567",
        password_hash="hashed_pw",
        email="test@example.com",
        name="Test User",
        kyc_status="approved",
        mfa_enabled=True,
        created_at=now,
        id="user-123",
    )

    # Assert
    assert user.phone == "+573001234567"
    assert user.password_hash == "hashed_pw"
    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.kyc_status == "approved"
    assert user.mfa_enabled is True
    assert user.created_at == now
    assert user.id == "user-123"


def test_user_when_id_set_then_is_mutable() -> None:
    """Edge case: El id de User es mutable (se asigna al persistir)."""
    # Arrange
    user = User(phone="+573001234567")

    # Act
    user.id = "new-id"

    # Assert
    assert user.id == "new-id"


def test_user_when_kyc_status_changed_then_reflects_new_value() -> None:
    """State transition: kyc_status puede cambiar."""
    # Arrange
    user = User(phone="+573001234567", kyc_status="pending")

    # Act
    user.kyc_status = "approved"

    # Assert
    assert user.kyc_status == "approved"
