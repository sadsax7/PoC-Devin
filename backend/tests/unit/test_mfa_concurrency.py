"""Tests de concurrencia para el limitador de intentos MFA."""

import asyncio

import pytest

from app.application.use_cases.verify_mfa_use_case import (
    MfaRateLimiter,
    TooManyMfaAttemptsError,
)


@pytest.mark.asyncio
async def test_rate_limiter_when_concurrent_attempts_then_all_counted() -> None:
    """Caso de concurrencia: multiples intentos simultaneos son contados."""
    # Arrange
    limiter = MfaRateLimiter()

    async def attempt() -> int:
        return limiter.check_and_increment("user_concurrent")

    # Act
    tasks = [attempt() for _ in range(3)]
    results = await asyncio.gather(*tasks)

    # Assert - todos los intentos fueron contados
    assert sorted(results) == [0, 1, 2]


@pytest.mark.asyncio
async def test_rate_limiter_when_concurrent_exceed_limit_then_raises() -> None:
    """Caso de concurrencia: exceder limite en concurrencia lanza error."""
    # Arrange
    limiter = MfaRateLimiter()
    for _ in range(3):
        limiter.check_and_increment("user_exceed")

    # Act & Assert
    with pytest.raises(TooManyMfaAttemptsError):
        limiter.check_and_increment("user_exceed")


@pytest.mark.asyncio
async def test_rate_limiter_when_concurrent_different_users_then_independent() -> None:
    """Caso de concurrencia: usuarios diferentes no se afectan mutuamente."""
    # Arrange
    limiter = MfaRateLimiter()

    async def attempt_user(user_id: str) -> int:
        return limiter.check_and_increment(user_id)

    # Act
    tasks = [
        attempt_user("userA"),
        attempt_user("userB"),
        attempt_user("userC"),
    ]
    results = await asyncio.gather(*tasks)

    # Assert - cada usuario tiene 2 intentos restantes
    assert all(r == 2 for r in results)
