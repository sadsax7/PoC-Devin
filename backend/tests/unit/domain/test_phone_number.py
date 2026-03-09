"""
Tests unitarios para el Value Object PhoneNumber.

Cubre: positivos, negativos, edge cases.
Referencia: HU-BE-01 AC#1, AC#4
"""

from __future__ import annotations

import pytest

from app.domain.value_objects.phone_number import PhoneNumber

# ============================================================
# Positivos
# ============================================================


class TestPhoneNumberValid:
    """Tests positivos de PhoneNumber."""

    def test_phone_number_when_valid_e164_then_created(self) -> None:
        """Un teléfono E.164 válido se crea correctamente."""
        phone = PhoneNumber("+573001234567")
        assert phone.value == "+573001234567"

    def test_phone_number_when_minimum_length_then_created(self) -> None:
        """El teléfono más corto válido (7 dígitos + país)."""
        phone = PhoneNumber("+1234567")
        assert phone.value == "+1234567"

    def test_phone_number_when_maximum_length_then_created(self) -> None:
        """El teléfono más largo válido (15 dígitos total)."""
        phone = PhoneNumber("+123456789012345")
        assert phone.value == "+123456789012345"


# ============================================================
# Negativos
# ============================================================


class TestPhoneNumberInvalid:
    """Tests negativos — formatos inválidos."""

    def test_phone_number_when_missing_plus_then_raises(self) -> None:
        """Sin signo + al inicio."""
        with pytest.raises(ValueError, match="E\\.164 format"):
            PhoneNumber("573001234567")

    def test_phone_number_when_starts_with_zero_then_raises(self) -> None:
        """El código de país no puede empezar con 0."""
        with pytest.raises(ValueError, match="E\\.164 format"):
            PhoneNumber("+0573001234567")

    def test_phone_number_when_too_short_then_raises(self) -> None:
        """Menos de 7 dígitos después del +."""
        with pytest.raises(ValueError, match="E\\.164 format"):
            PhoneNumber("+12345")

    def test_phone_number_when_too_long_then_raises(self) -> None:
        """Más de 15 dígitos después del +."""
        with pytest.raises(ValueError, match="E\\.164 format"):
            PhoneNumber("+1234567890123456")

    def test_phone_number_when_contains_letters_then_raises(self) -> None:
        """Letras en el número."""
        with pytest.raises(ValueError, match="E\\.164 format"):
            PhoneNumber("+57300ABC4567")

    def test_phone_number_when_empty_then_raises(self) -> None:
        """Cadena vacía."""
        with pytest.raises(ValueError, match="E\\.164 format"):
            PhoneNumber("")

    def test_phone_number_when_only_plus_then_raises(self) -> None:
        """Solo el signo +."""
        with pytest.raises(ValueError, match="E\\.164 format"):
            PhoneNumber("+")


# ============================================================
# Edge cases
# ============================================================


class TestPhoneNumberEdgeCases:
    """Edge cases para PhoneNumber."""

    def test_phone_number_is_frozen(self) -> None:
        """PhoneNumber es inmutable (frozen dataclass)."""
        phone = PhoneNumber("+573001234567")
        with pytest.raises(AttributeError):
            phone.value = "+1234567890"  # type: ignore[misc]

    def test_phone_number_ends_with_00(self) -> None:
        """Método ends_with para lógica KYC mock."""
        phone = PhoneNumber("+573001234500")
        assert phone.ends_with("00") is True

    def test_phone_number_ends_with_99(self) -> None:
        """Método ends_with para lógica KYC mock."""
        phone = PhoneNumber("+573001234599")
        assert phone.ends_with("99") is True

    def test_phone_number_does_not_end_with_00(self) -> None:
        phone = PhoneNumber("+573001234567")
        assert phone.ends_with("00") is False
