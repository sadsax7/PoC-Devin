"""Tests para el limitador de intentos MFA."""

import time
from unittest.mock import patch

import pytest

from app.application.use_cases.verify_mfa_use_case import (
    MfaRateLimiter,
    TooManyMfaAttemptsError,
)


def test_rate_limiter_when_first_attempt_then_returns_remaining_2() -> None:
    """Caso positivo: primer intento retorna 2 intentos restantes."""
    # Arrange
    limiter = MfaRateLimiter()

    # Act
    remaining = limiter.check_and_increment("user1")

    # Assert
    assert remaining == 2


def test_rate_limiter_when_second_attempt_then_returns_remaining_1() -> None:
    """Caso positivo: segundo intento retorna 1 intento restante."""
    # Arrange
    limiter = MfaRateLimiter()
    limiter.check_and_increment("user1")

    # Act
    remaining = limiter.check_and_increment("user1")

    # Assert
    assert remaining == 1


def test_rate_limiter_when_third_attempt_then_returns_remaining_0() -> None:
    """Caso positivo: tercer intento retorna 0 intentos restantes."""
    # Arrange
    limiter = MfaRateLimiter()
    limiter.check_and_increment("user1")
    limiter.check_and_increment("user1")

    # Act
    remaining = limiter.check_and_increment("user1")

    # Assert
    assert remaining == 0


def test_rate_limiter_when_fourth_attempt_then_raises_too_many() -> None:
    """Caso negativo: cuarto intento lanza error."""
    # Arrange
    limiter = MfaRateLimiter()
    for _ in range(3):
        limiter.check_and_increment("user1")

    # Act & Assert
    with pytest.raises(TooManyMfaAttemptsError):
        limiter.check_and_increment("user1")


def test_rate_limiter_when_clear_then_resets_counter() -> None:
    """Caso de estado: limpiar contador permite nuevos intentos."""
    # Arrange
    limiter = MfaRateLimiter()
    for _ in range(3):
        limiter.check_and_increment("user1")

    # Act
    limiter.clear("user1")
    remaining = limiter.check_and_increment("user1")

    # Assert
    assert remaining == 2


def test_rate_limiter_when_different_users_then_independent_counters() -> None:
    """Caso positivo: contadores independientes por usuario."""
    # Arrange
    limiter = MfaRateLimiter()
    for _ in range(3):
        limiter.check_and_increment("user1")

    # Act
    remaining = limiter.check_and_increment("user2")

    # Assert
    assert remaining == 2


def test_rate_limiter_when_expired_then_resets_automatically() -> None:
    """Caso de estado: contador expira despues de 5 minutos."""
    # Arrange
    limiter = MfaRateLimiter()
    limiter.check_and_increment("user1")
    limiter.check_and_increment("user1")
    limiter.check_and_increment("user1")

    # Act - simular paso de tiempo > 5 minutos
    with patch("time.monotonic", return_value=time.monotonic() + 301):
        remaining = limiter.check_and_increment("user1")

    # Assert
    assert remaining == 2


def test_rate_limiter_when_clear_nonexistent_user_then_no_error() -> None:
    """Edge case: limpiar usuario inexistente no lanza error."""
    # Arrange
    limiter = MfaRateLimiter()

    # Act & Assert - no debe lanzar excepcion
    limiter.clear("nonexistent")
