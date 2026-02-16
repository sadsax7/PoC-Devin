"""Tests unitarios para el value object PhoneNumber."""

import pytest

from app.domain.value_objects.phone_number import PhoneNumber


def test_phone_number_when_valid_e164_then_created() -> None:
    """Caso positivo: numero E.164 valido se crea correctamente."""
    # Arrange & Act
    phone = PhoneNumber("+573001234567")

    # Assert
    assert phone.value == "+573001234567"


def test_phone_number_when_missing_plus_then_raises_value_error() -> None:
    """Caso negativo: numero sin '+' lanza ValueError."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="does not match E.164 format"):
        PhoneNumber("573001234567")


def test_phone_number_when_too_short_then_raises_value_error() -> None:
    """Edge case: numero demasiado corto lanza ValueError."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="does not match E.164 format"):
        PhoneNumber("+12345")


def test_phone_number_when_too_long_then_raises_value_error() -> None:
    """Edge case: numero demasiado largo lanza ValueError."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="does not match E.164 format"):
        PhoneNumber("+1234567890123456")


def test_phone_number_when_contains_letters_then_raises_value_error() -> None:
    """Caso negativo: numero con letras lanza ValueError."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="does not match E.164 format"):
        PhoneNumber("+57300abc4567")


def test_phone_number_when_starts_with_zero_country_then_raises_value_error() -> None:
    """Edge case: codigo de pais que empieza con 0 lanza ValueError."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="does not match E.164 format"):
        PhoneNumber("+0573001234567")


def test_phone_number_when_empty_then_raises_value_error() -> None:
    """Edge case: string vacio lanza ValueError."""
    # Arrange & Act & Assert
    with pytest.raises(ValueError, match="does not match E.164 format"):
        PhoneNumber("")


def test_phone_number_ends_with_when_suffix_matches_then_true() -> None:
    """Caso positivo: ends_with retorna True con sufijo correcto."""
    # Arrange
    phone = PhoneNumber("+573001234500")

    # Act & Assert
    assert phone.ends_with("00") is True


def test_phone_number_ends_with_when_suffix_not_matches_then_false() -> None:
    """Caso negativo: ends_with retorna False con sufijo incorrecto."""
    # Arrange
    phone = PhoneNumber("+573001234567")

    # Act & Assert
    assert phone.ends_with("00") is False


def test_phone_number_equality_when_same_value_then_equal() -> None:
    """Caso positivo: dos PhoneNumber con mismo valor son iguales."""
    # Arrange
    phone_a = PhoneNumber("+573001234567")
    phone_b = PhoneNumber("+573001234567")

    # Assert
    assert phone_a == phone_b


def test_phone_number_equality_when_different_value_then_not_equal() -> None:
    """Caso negativo: dos PhoneNumber con distinto valor no son iguales."""
    # Arrange
    phone_a = PhoneNumber("+573001234567")
    phone_b = PhoneNumber("+573001234568")

    # Assert
    assert phone_a != phone_b


def test_phone_number_equality_when_compared_to_non_phone_then_not_equal() -> None:
    """Edge case: PhoneNumber comparado con otro tipo no es igual."""
    # Arrange
    phone = PhoneNumber("+573001234567")

    # Assert
    assert phone != "+573001234567"


def test_phone_number_hash_when_same_value_then_same_hash() -> None:
    """Caso positivo: mismos valores producen mismo hash."""
    # Arrange
    phone_a = PhoneNumber("+573001234567")
    phone_b = PhoneNumber("+573001234567")

    # Assert
    assert hash(phone_a) == hash(phone_b)


def test_phone_number_repr_then_contains_value() -> None:
    """Caso positivo: repr contiene el valor del numero."""
    # Arrange
    phone = PhoneNumber("+573001234567")

    # Assert
    assert "+573001234567" in repr(phone)


def test_phone_number_when_min_valid_length_then_created() -> None:
    """Edge case: numero con longitud minima valida (7 digitos)."""
    # Arrange & Act
    phone = PhoneNumber("+1234567")

    # Assert
    assert phone.value == "+1234567"


def test_phone_number_when_max_valid_length_then_created() -> None:
    """Edge case: numero con longitud maxima valida (15 digitos)."""
    # Arrange & Act
    phone = PhoneNumber("+123456789012345")

    # Assert
    assert phone.value == "+123456789012345"
