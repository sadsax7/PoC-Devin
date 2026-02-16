"""Tests unitarios para el servicio de dominio de registro."""

from app.domain.services.registration_service import (
    validate_email,
    validate_name,
    validate_password,
)


def test_validate_password_when_valid_then_returns_none() -> None:
    """Caso positivo: contrasena valida retorna None."""
    # Arrange & Act
    result = validate_password("Abcdef1!")

    # Assert
    assert result is None


def test_validate_password_when_too_short_then_returns_error() -> None:
    """Caso negativo: contrasena muy corta retorna error."""
    # Arrange & Act
    result = validate_password("Ab1!xyz")

    # Assert
    assert result is not None
    assert "at least 8" in result


def test_validate_password_when_too_long_then_returns_error() -> None:
    """Edge case: contrasena de 129 caracteres retorna error."""
    # Arrange
    password = "A" * 100 + "a" * 20 + "1" * 5 + "!" * 4

    # Act
    result = validate_password(password)

    # Assert
    assert result is not None
    assert "at most 128" in result


def test_validate_password_when_no_uppercase_then_returns_error() -> None:
    """Caso negativo: sin mayuscula retorna error."""
    # Arrange & Act
    result = validate_password("abcdef1!")

    # Assert
    assert result is not None
    assert "uppercase" in result


def test_validate_password_when_no_lowercase_then_returns_error() -> None:
    """Caso negativo: sin minuscula retorna error."""
    # Arrange & Act
    result = validate_password("ABCDEF1!")

    # Assert
    assert result is not None
    assert "lowercase" in result


def test_validate_password_when_no_digit_then_returns_error() -> None:
    """Caso negativo: sin digito retorna error."""
    # Arrange & Act
    result = validate_password("Abcdefg!")

    # Assert
    assert result is not None
    assert "digit" in result


def test_validate_password_when_no_special_char_then_returns_error() -> None:
    """Caso negativo: sin caracter especial retorna error."""
    # Arrange & Act
    result = validate_password("Abcdefg1")

    # Assert
    assert result is not None
    assert "special character" in result


def test_validate_password_when_exactly_min_length_then_returns_none() -> None:
    """Edge case: contrasena de exactamente 8 caracteres es valida."""
    # Arrange & Act
    result = validate_password("Abcde1!x")

    # Assert
    assert result is None


def test_validate_password_when_exactly_max_length_then_returns_none() -> None:
    """Edge case: contrasena de exactamente 128 caracteres es valida."""
    # Arrange
    password = "A" * 60 + "a" * 60 + "1234!@#$"

    # Act
    result = validate_password(password)

    # Assert
    assert result is None


def test_validate_email_when_valid_then_returns_none() -> None:
    """Caso positivo: email valido retorna None."""
    # Arrange & Act
    result = validate_email("user@example.com")

    # Assert
    assert result is None


def test_validate_email_when_invalid_format_then_returns_error() -> None:
    """Caso negativo: email invalido retorna error."""
    # Arrange & Act
    result = validate_email("not-an-email")

    # Assert
    assert result is not None
    assert "Invalid email" in result


def test_validate_email_when_too_long_then_returns_error() -> None:
    """Edge case: email de mas de 255 caracteres retorna error."""
    # Arrange
    email = "a" * 250 + "@b.com"

    # Act
    result = validate_email(email)

    # Assert
    assert result is not None
    assert "at most 255" in result


def test_validate_email_when_max_length_valid_then_returns_none() -> None:
    """Edge case: email de exactamente 255 caracteres es valido."""
    # Arrange
    local = "a" * 243
    email = f"{local}@example.com"
    assert len(email) == 255

    # Act
    result = validate_email(email)

    # Assert
    assert result is None


def test_validate_name_when_valid_then_returns_none() -> None:
    """Caso positivo: nombre valido retorna None."""
    # Arrange & Act
    result = validate_name("John Doe")

    # Assert
    assert result is None


def test_validate_name_when_too_long_then_returns_error() -> None:
    """Edge case: nombre de mas de 100 caracteres retorna error."""
    # Arrange
    name = "A" * 101

    # Act
    result = validate_name(name)

    # Assert
    assert result is not None
    assert "at most 100" in result


def test_validate_name_when_exactly_max_length_then_returns_none() -> None:
    """Edge case: nombre de exactamente 100 caracteres es valido."""
    # Arrange
    name = "A" * 100

    # Act
    result = validate_name(name)

    # Assert
    assert result is None
