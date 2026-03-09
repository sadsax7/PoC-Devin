"""
Tests unitarios para el caso de uso VerifyMfa.

Cubre: positivos, negativos, edge cases, brute-force.
Referencia: HU-BE-02 AC#2, BACKEND-GUIDELINES.md §5.1.7.1
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.application.dtos.auth_dtos import VerifyMfaInputDTO, VerifyMfaOutputDTO
from app.application.use_cases.verify_mfa import (
    InvalidMfaCodeError,
    InvalidTempTokenError,
    TooManyMfaAttemptsError,
    VerifyMfaUseCase,
)
from app.domain.entities.user import User
from app.domain.services.mfa_attempt_tracker import MfaAttemptTracker

# ============================================================
# Helpers
# ============================================================


def _build_use_case(
    *,
    verify_token_return: dict[str, object] | None = None,
    verify_token_side_effect: Exception | None = None,
    verify_code_return: bool = True,
    find_by_id_return: User | None = None,
    attempt_tracker: MfaAttemptTracker | None = None,
) -> VerifyMfaUseCase:
    """Construye un VerifyMfaUseCase con mocks configurados."""
    token_provider = MagicMock()
    if verify_token_side_effect is not None:
        token_provider.verify_token = MagicMock(
            side_effect=verify_token_side_effect,
        )
    else:
        default_claims: dict[str, object] = {
            "sub": "user123",
            "type": "temp",
            "mfa_pending": True,
        }
        token_provider.verify_token = MagicMock(
            return_value=verify_token_return or default_claims,
        )
    token_provider.generate_access_token = MagicMock(
        return_value="final.access.token",
    )
    token_provider.generate_refresh_token = MagicMock(
        return_value="final.refresh.token",
    )

    mfa_verifier = MagicMock()
    mfa_verifier.verify_code = MagicMock(return_value=verify_code_return)

    repo = MagicMock()
    if find_by_id_return is None:
        default_user = User(
            id="user123",
            phone="+573001234567",
            password_hash="$argon2id$hash",
            mfa_enabled=True,
        )
        repo.find_by_id = AsyncMock(return_value=default_user)
    else:
        repo.find_by_id = AsyncMock(return_value=find_by_id_return)

    publisher = MagicMock()
    publisher.publish = AsyncMock()

    tracker = attempt_tracker or MfaAttemptTracker()

    return VerifyMfaUseCase(
        token_provider=token_provider,
        mfa_verifier=mfa_verifier,
        user_repository=repo,
        event_publisher=publisher,
        attempt_tracker=tracker,
    )


def _valid_input(**overrides: object) -> VerifyMfaInputDTO:
    """Crea un DTO de entrada válido."""
    defaults: dict[str, object] = {
        "temp_token": "valid.temp.token",
        "code": "123456",
    }
    defaults.update(overrides)
    return VerifyMfaInputDTO(**defaults)  # type: ignore[arg-type]


# ============================================================
# Positivos (happy path)
# ============================================================


class TestVerifyMfaSuccess:
    """Tests positivos — verificación MFA exitosa."""

    @pytest.mark.asyncio
    async def test_execute_when_valid_code_then_returns_tokens(self) -> None:
        """Código MFA correcto retorna access y refresh tokens."""
        uc = _build_use_case()

        result = await uc.execute(_valid_input())

        assert isinstance(result, VerifyMfaOutputDTO)
        assert result.access_token == "final.access.token"
        assert result.refresh_token == "final.refresh.token"
        assert result.token_type == "Bearer"
        assert result.expires_in == 1800

    @pytest.mark.asyncio
    async def test_execute_when_valid_then_publishes_success_event(
        self,
    ) -> None:
        """Se publica evento MfaVerificationSuccess."""
        uc = _build_use_case()

        await uc.execute(_valid_input())

        call_args = uc._event_publisher.publish.call_args
        assert call_args[0][0] == "MfaVerificationSuccess"
        assert call_args[0][1]["user_id"] == "user123"

    @pytest.mark.asyncio
    async def test_execute_when_valid_then_clears_attempt_tracker(
        self,
    ) -> None:
        """Verificación exitosa limpia el tracker de intentos."""
        tracker = MfaAttemptTracker()
        tracker.record_failure("user123")
        uc = _build_use_case(attempt_tracker=tracker)

        await uc.execute(_valid_input())

        assert not tracker.is_blocked("user123")

    @pytest.mark.asyncio
    async def test_execute_when_valid_then_uses_user_phone_for_token(
        self,
    ) -> None:
        """El access token se genera con el phone del usuario."""
        user = User(
            id="user123",
            phone="+573009999999",
            password_hash="$argon2id$hash",
            mfa_enabled=True,
        )
        uc = _build_use_case(find_by_id_return=user)

        await uc.execute(_valid_input())

        uc._token_provider.generate_access_token.assert_called_once_with("user123", "+573009999999")


# ============================================================
# Negativos (error handling)
# ============================================================


class TestVerifyMfaNegative:
    """Tests negativos — errores de verificación."""

    @pytest.mark.asyncio
    async def test_execute_when_expired_token_then_raises(self) -> None:
        """Token expirado lanza InvalidTempTokenError."""
        uc = _build_use_case(
            verify_token_side_effect=ValueError("Token has expired"),
        )

        with pytest.raises(InvalidTempTokenError, match="expired"):
            await uc.execute(_valid_input())

    @pytest.mark.asyncio
    async def test_execute_when_invalid_token_then_raises(self) -> None:
        """Token inválido lanza InvalidTempTokenError."""
        uc = _build_use_case(
            verify_token_side_effect=ValueError("Invalid token"),
        )

        with pytest.raises(InvalidTempTokenError, match="expired"):
            await uc.execute(_valid_input())

    @pytest.mark.asyncio
    async def test_execute_when_token_type_not_temp_then_raises(self) -> None:
        """Token con type != temp lanza InvalidTempTokenError."""
        uc = _build_use_case(
            verify_token_return={
                "sub": "user123",
                "type": "access",
                "mfa_pending": True,
            },
        )

        with pytest.raises(InvalidTempTokenError):
            await uc.execute(_valid_input())

    @pytest.mark.asyncio
    async def test_execute_when_mfa_pending_false_then_raises(self) -> None:
        """Token sin mfa_pending=true lanza InvalidTempTokenError."""
        uc = _build_use_case(
            verify_token_return={
                "sub": "user123",
                "type": "temp",
                "mfa_pending": False,
            },
        )

        with pytest.raises(InvalidTempTokenError):
            await uc.execute(_valid_input())

    @pytest.mark.asyncio
    async def test_execute_when_wrong_code_then_raises_with_remaining(
        self,
    ) -> None:
        """Código incorrecto lanza InvalidMfaCodeError con intentos restantes."""
        uc = _build_use_case(verify_code_return=False)

        with pytest.raises(InvalidMfaCodeError) as exc_info:
            await uc.execute(_valid_input(code="000000"))

        assert exc_info.value.attempts_remaining == 2

    @pytest.mark.asyncio
    async def test_execute_when_wrong_code_then_publishes_failure_event(
        self,
    ) -> None:
        """Código incorrecto publica MfaVerificationFailed."""
        uc = _build_use_case(verify_code_return=False)

        with pytest.raises(InvalidMfaCodeError):
            await uc.execute(_valid_input(code="999999"))

        call_args = uc._event_publisher.publish.call_args
        assert call_args[0][0] == "MfaVerificationFailed"


# ============================================================
# Brute-force protection
# ============================================================


class TestVerifyMfaBruteForce:
    """Tests de protección contra fuerza bruta."""

    @pytest.mark.asyncio
    async def test_execute_when_max_attempts_then_raises_too_many(
        self,
    ) -> None:
        """3 intentos fallidos → TooManyMfaAttemptsError."""
        tracker = MfaAttemptTracker(max_attempts=3)
        tracker.record_failure("user123")
        tracker.record_failure("user123")
        # Third failure comes from the use case
        uc = _build_use_case(
            verify_code_return=False,
            attempt_tracker=tracker,
        )

        with pytest.raises(TooManyMfaAttemptsError, match="Too many"):
            await uc.execute(_valid_input(code="000000"))

    @pytest.mark.asyncio
    async def test_execute_when_blocked_then_raises_immediately(
        self,
    ) -> None:
        """Usuario bloqueado → error inmediato sin verificar código."""
        tracker = MfaAttemptTracker(max_attempts=3)
        tracker.record_failure("user123")
        tracker.record_failure("user123")
        tracker.record_failure("user123")
        uc = _build_use_case(attempt_tracker=tracker)

        with pytest.raises(TooManyMfaAttemptsError, match="Too many"):
            await uc.execute(_valid_input())

        uc._mfa_verifier.verify_code.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_when_valid_after_failures_then_clears(
        self,
    ) -> None:
        """Código válido después de fallos limpia el tracker."""
        tracker = MfaAttemptTracker(max_attempts=3)
        tracker.record_failure("user123")
        uc = _build_use_case(
            verify_code_return=True,
            attempt_tracker=tracker,
        )

        result = await uc.execute(_valid_input())

        assert isinstance(result, VerifyMfaOutputDTO)
        assert not tracker.is_blocked("user123")


# ============================================================
# Edge cases
# ============================================================


class TestVerifyMfaEdgeCases:
    """Edge cases para verificación MFA."""

    @pytest.mark.asyncio
    async def test_execute_when_user_not_found_then_uses_empty_phone(
        self,
    ) -> None:
        """Si find_by_id retorna None, phone es cadena vacía."""
        uc = _build_use_case(find_by_id_return=None)  # type: ignore[arg-type]
        uc._user_repository.find_by_id = AsyncMock(return_value=None)

        result = await uc.execute(_valid_input())

        uc._token_provider.generate_access_token.assert_called_once_with("user123", "")
        assert isinstance(result, VerifyMfaOutputDTO)

    @pytest.mark.asyncio
    async def test_execute_when_sub_missing_then_empty_user_id(self) -> None:
        """Si claims no tiene sub, user_id es cadena vacía."""
        uc = _build_use_case(
            verify_token_return={
                "type": "temp",
                "mfa_pending": True,
            },
        )

        result = await uc.execute(_valid_input())

        assert isinstance(result, VerifyMfaOutputDTO)
