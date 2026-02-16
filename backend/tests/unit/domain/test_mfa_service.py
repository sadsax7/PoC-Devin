"""Tests para el servicio de dominio de MFA."""

from app.domain.services.mfa_service import verify_mfa_code


def test_verify_mfa_code_when_correct_code_then_returns_true() -> None:
    """Caso positivo: codigo MFA correcto."""
    assert verify_mfa_code("123456") is True


def test_verify_mfa_code_when_wrong_code_then_returns_false() -> None:
    """Caso negativo: codigo MFA incorrecto."""
    assert verify_mfa_code("000000") is False


def test_verify_mfa_code_when_empty_code_then_returns_false() -> None:
    """Edge case: codigo vacio."""
    assert verify_mfa_code("") is False


def test_verify_mfa_code_when_partial_match_then_returns_false() -> None:
    """Edge case: coincidencia parcial del codigo."""
    assert verify_mfa_code("12345") is False


def test_verify_mfa_code_when_extra_digits_then_returns_false() -> None:
    """Edge case: codigo con digitos extra."""
    assert verify_mfa_code("1234567") is False
