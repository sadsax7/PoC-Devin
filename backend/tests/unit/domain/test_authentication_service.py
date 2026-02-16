"""Tests para el servicio de dominio de autenticacion."""

from app.domain.services.authentication_service import (
    is_account_locked,
    requires_mfa,
    validate_login_password,
)


def test_validate_login_password_when_valid_length_then_returns_true() -> None:
    """Caso positivo: contrasena con longitud valida."""
    assert validate_login_password("Ab1!xxxx") is True


def test_validate_login_password_when_too_short_then_returns_false() -> None:
    """Caso negativo: contrasena demasiado corta."""
    assert validate_login_password("Ab1!xxx") is False


def test_validate_login_password_when_too_long_then_returns_false() -> None:
    """Caso negativo: contrasena demasiado larga."""
    assert validate_login_password("a" * 129) is False


def test_validate_login_password_when_min_length_then_returns_true() -> None:
    """Edge case: contrasena exactamente en longitud minima."""
    assert validate_login_password("12345678") is True


def test_validate_login_password_when_max_length_then_returns_true() -> None:
    """Edge case: contrasena exactamente en longitud maxima."""
    assert validate_login_password("a" * 128) is True


def test_validate_login_password_when_empty_then_returns_false() -> None:
    """Edge case: contrasena vacia."""
    assert validate_login_password("") is False


def test_is_account_locked_when_rejected_then_returns_true() -> None:
    """Caso positivo: cuenta bloqueada por rechazo KYC."""
    assert is_account_locked("rejected") is True


def test_is_account_locked_when_approved_then_returns_false() -> None:
    """Caso negativo: cuenta con KYC aprobado."""
    assert is_account_locked("approved") is False


def test_is_account_locked_when_pending_then_returns_false() -> None:
    """Caso negativo: cuenta con KYC pendiente."""
    assert is_account_locked("pending") is False


def test_requires_mfa_when_enabled_then_returns_true() -> None:
    """Caso positivo: MFA habilitado."""
    assert requires_mfa(True) is True


def test_requires_mfa_when_disabled_then_returns_false() -> None:
    """Caso negativo: MFA deshabilitado."""
    assert requires_mfa(False) is False
