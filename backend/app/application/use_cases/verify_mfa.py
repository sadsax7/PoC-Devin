"""
Caso de uso: Verificar código MFA.

Valida el temp_token, verifica el código MFA y emite tokens
finales de acceso. Incluye protección contra fuerza bruta.

Referencia: HU-BE-02 AC#2.
"""

from __future__ import annotations

import logging

from app.application.dtos.auth_dtos import VerifyMfaInputDTO, VerifyMfaOutputDTO
from app.domain.ports.event_publisher_port import EventPublisherPort
from app.domain.ports.mfa_verifier_port import MfaVerifierPort
from app.domain.ports.token_provider_port import TokenProviderPort
from app.domain.ports.user_repository import UserRepository
from app.domain.services.mfa_attempt_tracker import MfaAttemptTracker

logger = logging.getLogger(__name__)


class InvalidMfaCodeError(Exception):
    """Código MFA incorrecto.

    Attributes:
        attempts_remaining: Intentos restantes.
    """

    def __init__(self, attempts_remaining: int) -> None:
        """Inicializa con intentos restantes.

        Args:
            attempts_remaining: Cuántos intentos quedan.
        """
        self.attempts_remaining = attempts_remaining
        super().__init__("Invalid MFA code")


class TooManyMfaAttemptsError(Exception):
    """Demasiados intentos fallidos de MFA."""


class InvalidTempTokenError(Exception):
    """Temp token inválido o expirado."""


class VerifyMfaUseCase:
    """Caso de uso para verificación MFA.

    Flujo:
    1. Decodifica temp_token y extrae user_id.
    2. Verifica que no esté bloqueado por intentos.
    3. Verifica código MFA.
    4. Emite tokens finales o registra fallo.

    Attributes:
        _token_provider: Puerto de tokens JWT.
        _mfa_verifier: Puerto de verificación MFA.
        _user_repository: Puerto de persistencia.
        _event_publisher: Puerto de eventos.
        _attempt_tracker: Rastreador de intentos en memoria.
    """

    def __init__(
        self,
        token_provider: TokenProviderPort,
        mfa_verifier: MfaVerifierPort,
        user_repository: UserRepository,
        event_publisher: EventPublisherPort,
        attempt_tracker: MfaAttemptTracker,
    ) -> None:
        """Inicializa el caso de uso con sus dependencias.

        Args:
            token_provider: Puerto de tokens JWT.
            mfa_verifier: Puerto de verificación MFA.
            user_repository: Puerto de persistencia.
            event_publisher: Puerto de eventos.
            attempt_tracker: Rastreador de intentos MFA.
        """
        self._token_provider = token_provider
        self._mfa_verifier = mfa_verifier
        self._user_repository = user_repository
        self._event_publisher = event_publisher
        self._attempt_tracker = attempt_tracker

    async def execute(self, input_dto: VerifyMfaInputDTO) -> VerifyMfaOutputDTO:
        """Ejecuta la verificación MFA.

        Args:
            input_dto: Datos de verificación (temp_token, code).

        Returns:
            VerifyMfaOutputDTO con tokens finales.

        Raises:
            InvalidTempTokenError: Token inválido o expirado.
            TooManyMfaAttemptsError: Exceso de intentos.
            InvalidMfaCodeError: Código incorrecto.
        """
        try:
            claims = self._token_provider.verify_token(input_dto.temp_token)
        except ValueError:
            raise InvalidTempTokenError("Temporary token expired, please login again") from None

        token_type = claims.get("type")
        mfa_pending = claims.get("mfa_pending")
        if token_type != "temp" or mfa_pending is not True:  # noqa: S105
            raise InvalidTempTokenError("Temporary token expired, please login again")

        user_id = str(claims.get("sub", ""))

        if self._attempt_tracker.is_blocked(user_id):
            logger.info(
                '{"event":"mfa_blocked","user_id":"%s"}',
                user_id,
            )
            raise TooManyMfaAttemptsError("Too many failed MFA attempts, please login again")

        if not self._mfa_verifier.verify_code(input_dto.code):
            remaining = self._attempt_tracker.record_failure(user_id)
            logger.info(
                '{"event":"mfa_failed","user_id":"%s","remaining":%d}',
                user_id,
                remaining,
            )
            await self._event_publisher.publish(
                "MfaVerificationFailed",
                {"user_id": user_id, "attempts_remaining": remaining},
            )
            if remaining == 0:
                raise TooManyMfaAttemptsError("Too many failed MFA attempts, please login again")
            raise InvalidMfaCodeError(attempts_remaining=remaining)

        self._attempt_tracker.clear(user_id)

        user = await self._user_repository.find_by_id(user_id)
        phone = user.phone if user else ""

        access_token = self._token_provider.generate_access_token(user_id, phone)
        refresh_token = self._token_provider.generate_refresh_token(user_id)

        logger.info(
            '{"event":"mfa_success","user_id":"%s","ip":"127.0.0.1"}',
            user_id,
        )
        await self._event_publisher.publish(
            "MfaVerificationSuccess",
            {"user_id": user_id, "ip": "127.0.0.1"},
        )

        return VerifyMfaOutputDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )
