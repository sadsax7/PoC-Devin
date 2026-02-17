"""Caso de uso para verificacion de codigo MFA.

Orquesta el flujo de verificacion MFA: validacion del token temporal,
verificacion del codigo y emision de tokens finales.
"""

import logging
import time
from typing import Dict, Tuple

from app.application.dtos.verify_mfa_dto import VerifyMfaInputDTO, VerifyMfaOutputDTO
from app.domain.ports.token_provider_port import (
    TokenExpiredException,
    TokenInvalidException,
    TokenProviderPort,
)
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.services.mfa_service import verify_mfa_code
from app.shared.audit_logger import audit_log

logger = logging.getLogger(__name__)

_MAX_MFA_ATTEMPTS = 3
_MFA_LOCKOUT_SECONDS = 300


class InvalidMfaCodeError(Exception):
    """Error cuando el codigo MFA es incorrecto.

    Attributes:
        attempts_remaining: Intentos restantes antes del bloqueo.
    """

    def __init__(self, attempts_remaining: int) -> None:
        """Inicializa el error con intentos restantes.

        Args:
            attempts_remaining: Numero de intentos restantes.
        """
        self.attempts_remaining = attempts_remaining
        super().__init__("Invalid MFA code")


class TempTokenExpiredError(Exception):
    """Error cuando el token temporal ha expirado."""


class TooManyMfaAttemptsError(Exception):
    """Error cuando se exceden los intentos de MFA permitidos."""


class MfaRateLimiter:
    """Limitador de intentos de MFA en memoria.

    Rastrea intentos fallidos por usuario y aplica bloqueo
    despues de exceder el maximo permitido.
    """

    def __init__(self) -> None:
        """Inicializa el limitador con almacenamiento en memoria."""
        self._attempts: Dict[str, Tuple[int, float]] = {}

    def check_and_increment(self, user_id: str) -> int:
        """Verifica e incrementa el contador de intentos fallidos.

        Args:
            user_id: Identificador del usuario.

        Returns:
            Numero de intentos restantes.

        Raises:
            TooManyMfaAttemptsError: Si se exceden los intentos permitidos.
        """
        now = time.monotonic()
        self._cleanup_expired(user_id, now)

        attempts, first_attempt_time = self._attempts.get(user_id, (0, now))

        if attempts >= _MAX_MFA_ATTEMPTS:
            raise TooManyMfaAttemptsError("Too many failed MFA attempts, please login again")

        new_attempts = attempts + 1
        self._attempts[user_id] = (new_attempts, first_attempt_time)
        return _MAX_MFA_ATTEMPTS - new_attempts

    def clear(self, user_id: str) -> None:
        """Limpia el contador de intentos para un usuario.

        Args:
            user_id: Identificador del usuario.
        """
        self._attempts.pop(user_id, None)

    def _cleanup_expired(self, user_id: str, now: float) -> None:
        """Limpia contadores expirados por inactividad.

        Args:
            user_id: Identificador del usuario.
            now: Tiempo actual en segundos monotonicos.
        """
        if user_id in self._attempts:
            _, first_attempt_time = self._attempts[user_id]
            if now - first_attempt_time > _MFA_LOCKOUT_SECONDS:
                del self._attempts[user_id]


class VerifyMfaUseCase:
    """Caso de uso para verificar codigo MFA y emitir tokens finales.

    Coordina la validacion del token temporal, verificacion del
    codigo MFA y emision de access y refresh tokens.
    """

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        token_provider: TokenProviderPort,
        rate_limiter: "MfaRateLimiter",
    ) -> None:
        """Inicializa el caso de uso con sus dependencias.

        Args:
            user_repository: Puerto del repositorio de usuarios.
            token_provider: Puerto del proveedor de tokens.
            rate_limiter: Limitador de intentos MFA.
        """
        self._user_repository = user_repository
        self._token_provider = token_provider
        self._rate_limiter = rate_limiter

    async def execute(self, input_dto: VerifyMfaInputDTO) -> VerifyMfaOutputDTO:
        """Ejecuta el flujo de verificacion MFA.

        Args:
            input_dto: Datos de entrada de la verificacion.

        Returns:
            DTO con access y refresh tokens.

        Raises:
            TempTokenExpiredError: Si el token temporal ha expirado.
            TooManyMfaAttemptsError: Si se exceden los intentos.
            InvalidMfaCodeError: Si el codigo MFA es incorrecto.
        """
        claims = self._decode_temp_token(input_dto.temp_token)
        user_id = str(claims["sub"])

        remaining = self._rate_limiter.check_and_increment(user_id)

        if not verify_mfa_code(input_dto.code):
            audit_log(
                event="mfa_verify_failed",
                user_id=user_id,
                reason="invalid_code",
                ip="127.0.0.1",
            )
            raise InvalidMfaCodeError(attempts_remaining=remaining)

        self._rate_limiter.clear(user_id)

        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise TempTokenExpiredError("Temporary token expired, please login again")

        access_token = self._token_provider.create_access_token(user_id, user.phone)
        refresh_token = self._token_provider.create_refresh_token(user_id)

        audit_log(
            event="mfa_verify_success",
            user_id=user_id,
            ip="127.0.0.1",
        )

        return VerifyMfaOutputDTO(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=1800,
        )

    def _decode_temp_token(self, token: str) -> Dict[str, object]:
        """Decodifica y valida el token temporal de MFA.

        Args:
            token: Token JWT temporal.

        Returns:
            Claims del token decodificado.

        Raises:
            TempTokenExpiredError: Si el token es invalido o expirado.
        """
        try:
            claims = self._token_provider.decode_token(token)
        except (TokenExpiredException, TokenInvalidException) as exc:
            raise TempTokenExpiredError("Temporary token expired, please login again") from exc

        if claims.get("type") != "temp" or not claims.get("mfa_pending"):
            raise TempTokenExpiredError("Temporary token expired, please login again")

        return claims
