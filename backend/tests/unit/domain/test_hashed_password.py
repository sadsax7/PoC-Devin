"""
Tests unitarios para el Value Object HashedPassword.

Cubre: positivos, negativos, edge cases.
Referencia: HU-BE-01 AC#2
"""

from __future__ import annotations

import pytest

from app.domain.value_objects.hashed_password import HashedPassword

# ============================================================
# HashedPassword creation
# ============================================================


class TestHashedPasswordCreation:
    """Tests de creación del wrapper HashedPassword."""

    def test_hashed_password_when_valid_hash_then_created(self) -> None:
        """Wrappea un hash correctamente."""
        hp = HashedPassword("$argon2id$v=19$hash")
        assert hp.value == "$argon2id$v=19$hash"

    def test_hashed_password_is_frozen(self) -> None:
        """HashedPassword es inmutable."""
        hp = HashedPassword("$argon2id$v=19$hash")
        with pytest.raises(AttributeError):
            hp.value = "other"  # type: ignore[misc]


# ============================================================
# validate_plain_password — positivos
# ============================================================


class TestValidatePasswordValid:
    """Tests positivos de validación de contraseña."""

    def test_validate_when_valid_password_then_no_errors(self) -> None:
        """Contraseña válida no produce errores."""
        errors = HashedPassword.validate_plain_password("Str0ng!Pass")
        assert errors == []

    def test_validate_when_exactly_8_chars_then_valid(self) -> None:
        """Contraseña de exactamente 8 caracteres."""
        errors = HashedPassword.validate_plain_password("Aa1!xxxx")
        assert errors == []

    def test_validate_when_128_chars_then_valid(self) -> None:
        """Contraseña de exactamente 128 caracteres."""
        pwd = "Aa1!" + "x" * 124
        errors = HashedPassword.validate_plain_password(pwd)
        assert errors == []


# ============================================================
# validate_plain_password — negativos
# ============================================================


class TestValidatePasswordInvalid:
    """Tests negativos — contraseñas que no cumplen reglas."""

    def test_validate_when_too_short_then_error(self) -> None:
        """Menos de 8 caracteres."""
        errors = HashedPassword.validate_plain_password("Aa1!xxx")
        assert any("at least 8" in e for e in errors)

    def test_validate_when_too_long_then_error(self) -> None:
        """Más de 128 caracteres."""
        pwd = "Aa1!" + "x" * 125
        errors = HashedPassword.validate_plain_password(pwd)
        assert any("at most 128" in e for e in errors)

    def test_validate_when_no_uppercase_then_error(self) -> None:
        """Sin mayúsculas."""
        errors = HashedPassword.validate_plain_password("str0ng!pass")
        assert any("uppercase" in e for e in errors)

    def test_validate_when_no_lowercase_then_error(self) -> None:
        """Sin minúsculas."""
        errors = HashedPassword.validate_plain_password("STR0NG!PASS")
        assert any("lowercase" in e for e in errors)

    def test_validate_when_no_digit_then_error(self) -> None:
        """Sin dígitos."""
        errors = HashedPassword.validate_plain_password("Strong!Pass")
        assert any("digit" in e for e in errors)

    def test_validate_when_no_special_then_error(self) -> None:
        """Sin caracteres especiales."""
        errors = HashedPassword.validate_plain_password("Str0ngPassw")
        assert any("special" in e for e in errors)

    def test_validate_when_all_missing_then_multiple_errors(self) -> None:
        """Todos los requisitos fallando a la vez."""
        errors = HashedPassword.validate_plain_password("aaaa")
        assert len(errors) >= 3  # too short + no uppercase + no digit + no special


# ============================================================
# Edge cases
# ============================================================


class TestValidatePasswordEdgeCases:
    """Edge cases para validación de contraseña."""

    def test_validate_when_empty_string_then_errors(self) -> None:
        """Cadena vacía produce múltiples errores."""
        errors = HashedPassword.validate_plain_password("")
        assert len(errors) >= 1

    def test_validate_when_special_chars_only_then_errors(self) -> None:
        """Solo caracteres especiales falla mayúscula, minúscula y dígito."""
        errors = HashedPassword.validate_plain_password("!@#$%^&*")
        assert any("uppercase" in e for e in errors)
        assert any("lowercase" in e for e in errors)
        assert any("digit" in e for e in errors)

    def test_validate_when_unicode_special_then_no_special_error(self) -> None:
        """Caracteres unicode no cuentan como especiales ASCII."""
        errors = HashedPassword.validate_plain_password("Str0ngPässword")
        # ä is not an ASCII special character per the regex
        assert any("special" in e for e in errors)
