"""Tests para el value object JwtToken."""

import pytest

from app.domain.value_objects.jwt_token import JwtToken


def test_jwt_token_when_valid_value_then_created() -> None:
    """Caso positivo: token con valor valido."""
    token = JwtToken("eyJhbGciOiJSUzI1NiJ9.abc.xyz")
    assert token.value == "eyJhbGciOiJSUzI1NiJ9.abc.xyz"


def test_jwt_token_when_empty_then_raises_value_error() -> None:
    """Caso negativo: token vacio."""
    with pytest.raises(ValueError, match="JWT token cannot be empty"):
        JwtToken("")


def test_jwt_token_last_four_when_called_then_returns_last_4_chars() -> None:
    """Caso positivo: ultimos 4 caracteres para logging seguro."""
    token = JwtToken("abcdefghijklmnop")
    assert token.last_four() == "mnop"


def test_jwt_token_eq_when_same_value_then_equal() -> None:
    """Caso positivo: tokens con mismo valor son iguales."""
    token1 = JwtToken("abc123")
    token2 = JwtToken("abc123")
    assert token1 == token2


def test_jwt_token_eq_when_different_value_then_not_equal() -> None:
    """Caso negativo: tokens con diferente valor no son iguales."""
    token1 = JwtToken("abc123")
    token2 = JwtToken("xyz789")
    assert token1 != token2


def test_jwt_token_eq_when_different_type_then_not_equal() -> None:
    """Edge case: comparacion con tipo diferente."""
    token = JwtToken("abc123")
    assert token != "abc123"


def test_jwt_token_hash_when_same_value_then_same_hash() -> None:
    """Caso positivo: tokens iguales tienen mismo hash."""
    token1 = JwtToken("abc123")
    token2 = JwtToken("abc123")
    assert hash(token1) == hash(token2)


def test_jwt_token_repr_when_called_then_hides_full_value() -> None:
    """Caso de seguridad: repr no expone token completo."""
    token = JwtToken("eyJhbGciOiJSUzI1NiJ9.abc.xyz")
    repr_str = repr(token)
    assert "eyJhbGciOiJSUzI1NiJ9" not in repr_str
    assert ".xyz" in repr_str


def test_jwt_token_when_short_value_then_last_four_works() -> None:
    """Edge case: token corto funciona correctamente."""
    token = JwtToken("ab")
    assert token.last_four() == "ab"
