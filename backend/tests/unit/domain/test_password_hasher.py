"""Tests unitarios para el hasher de contrasenas Argon2."""

from app.adapters.outbound.security.password_hasher_impl import Argon2PasswordHasher


def test_argon2_hasher_when_valid_password_then_returns_hash() -> None:
    """Caso positivo: contrasena valida retorna hash no vacio."""
    # Arrange
    hasher = Argon2PasswordHasher()

    # Act
    result = hasher.hash_password("ValidPass1!")

    # Assert
    assert result != ""
    assert result != "ValidPass1!"
    assert "$argon2" in result


def test_argon2_hasher_when_same_password_then_different_hashes() -> None:
    """Seguridad: misma contrasena genera hashes diferentes (salt unico)."""
    # Arrange
    hasher = Argon2PasswordHasher()

    # Act
    hash1 = hasher.hash_password("ValidPass1!")
    hash2 = hasher.hash_password("ValidPass1!")

    # Assert
    assert hash1 != hash2


def test_argon2_hasher_when_empty_password_then_returns_hash() -> None:
    """Edge case: contrasena vacia genera hash (validacion es en dominio)."""
    # Arrange
    hasher = Argon2PasswordHasher()

    # Act
    result = hasher.hash_password("")

    # Assert
    assert result != ""
    assert "$argon2" in result


def test_argon2_hasher_when_long_password_then_returns_hash() -> None:
    """Edge case: contrasena larga genera hash correctamente."""
    # Arrange
    hasher = Argon2PasswordHasher()
    password = "A" * 500

    # Act
    result = hasher.hash_password(password)

    # Assert
    assert result != ""
    assert "$argon2" in result
