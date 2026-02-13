"""
Tests unitarios para la entidad User del dominio.
"""

from app.domain.entities.user import User


def test_user_when_created_with_email_then_has_correct_attributes() -> None:
    """Caso positivo: User con email tiene atributos correctos."""
    # Arrange & Act
    user = User(email="test@example.com")

    # Assert
    assert user.email == "test@example.com"
    assert user.password_hash == ""
    assert user.full_name == ""
    assert user.is_active is True
    assert user.id is None


def test_user_when_created_with_all_fields_then_has_correct_attributes() -> None:
    """Caso positivo: User con todos los campos tiene atributos correctos."""
    # Arrange & Act
    user = User(
        email="test@example.com",
        password_hash="hashed_pw",
        full_name="Test User",
        is_active=False,
        id="user-123",
    )

    # Assert
    assert user.email == "test@example.com"
    assert user.password_hash == "hashed_pw"
    assert user.full_name == "Test User"
    assert user.is_active is False
    assert user.id == "user-123"


def test_user_when_id_set_then_is_mutable() -> None:
    """Edge case: El id de User es mutable (se asigna al persistir)."""
    # Arrange
    user = User(email="test@example.com")

    # Act
    user.id = "new-id"

    # Assert
    assert user.id == "new-id"
