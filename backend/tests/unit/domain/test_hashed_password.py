"""Tests unitarios para el value object HashedPassword."""

import pytest

from app.domain.value_objects.hashed_password import HashedPassword


def test_hashed_password_when_valid_hash_then_created() -> None:
    """Caso positivo: hash valido se crea correctamente."""
    # Arrange & Act
    hp = HashedPassword("$argon2id$v=19$m=65536,t=3,p=4$abc123")

    # Assert
    assert hp.value == "$argon2id$v=19$m=65536,t=3,p=4$abc123"


def test_hashed_password_when_empty_then_raises_value_error() -> None:
    """Caso negativo: hash vacio lanza ValueError."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="cannot be empty"):
        HashedPassword("")


def test_hashed_password_equality_when_same_value_then_equal() -> None:
    """Caso positivo: dos HashedPassword con mismo valor son iguales."""
    # Arrange
    hp_a = HashedPassword("hash_abc")
    hp_b = HashedPassword("hash_abc")

    # Assert
    assert hp_a == hp_b


def test_hashed_password_equality_when_different_value_then_not_equal() -> None:
    """Caso negativo: dos HashedPassword con distinto valor no son iguales."""
    # Arrange
    hp_a = HashedPassword("hash_abc")
    hp_b = HashedPassword("hash_xyz")

    # Assert
    assert hp_a != hp_b


def test_hashed_password_equality_when_compared_to_string_then_not_equal() -> None:
    """Edge case: HashedPassword comparado con string no es igual."""
    # Arrange
    hp = HashedPassword("hash_abc")

    # Assert
    assert hp != "hash_abc"


def test_hashed_password_repr_then_does_not_expose_hash() -> None:
    """Seguridad: repr no expone el hash real."""
    # Arrange
    hp = HashedPassword("super_secret_hash")

    # Assert
    assert "super_secret_hash" not in repr(hp)
    assert "***" in repr(hp)


def test_hashed_password_hash_when_same_value_then_same_hash() -> None:
    """Caso positivo: mismos valores producen mismo hash de Python."""
    # Arrange
    hp_a = HashedPassword("hash_abc")
    hp_b = HashedPassword("hash_abc")

    # Assert
    assert hash(hp_a) == hash(hp_b)
