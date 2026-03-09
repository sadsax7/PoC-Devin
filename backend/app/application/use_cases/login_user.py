"""
Caso de uso: Login de usuario.

Valida credenciales contra MongoDB y gestiona el flujo de
autenticación bifurcado (con/sin MFA).

Referencia: HU-BE-02 AC#1.
"""

from __future__ import annotations

import logging

from app.application.dtos.auth_dtos import (
    LoginInputDTO,
    LoginMfaRequiredDTO,
    LoginOutputDTO,
)
from app.domain.ports.event_publisher_port import EventPublisherPort
from app.domain.ports.password_hasher_port import PasswordHasherPort
from app.domain.ports.token_provider_port import TokenProviderPort
from app.domain.ports.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    """El teléfono no está registrado."""


class InvalidCredentialsError(Exception):
    """Contraseña incorrecta."""


class AccountLockedError(Exception):
    """Cuenta bloqueada por KYC rechazado."""


class LoginUserUseCase:
    """Caso de uso para autenticación de usuarios.

    Flujo:
    1. Busca usuario por teléfono.
    2. Verifica estado KYC (no bloqueado).
    3. Verifica contraseña con Argon2.
    4. Emite tokens según estado MFA.

    Attributes:
        _user_repository: Puerto de persistencia.
        _password_hasher: Puerto de hashing.
        _token_provider: Puerto de tokens JWT.
        _event_publisher: Puerto de eventos de dominio.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherPort,
        token_provider: TokenProviderPort,
        event_publisher: EventPublisherPort,
    ) -> None:
        """Inicializa el caso de uso con sus dependencias.

        Args:
            user_repository: Puerto de persistencia.
            password_hasher: Puerto de hashing.
            token_provider: Puerto de tokens JWT.
            event_publisher: Puerto de eventos de dominio.
        """
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider
        self._event_publisher = event_publisher

    async def execute(self, input_dto: LoginInputDTO) -> LoginOutputDTO | LoginMfaRequiredDTO:
        """Ejecuta el flujo de login.

        Args:
            input_dto: Datos de login (phone, password).

        Returns:
            LoginOutputDTO si MFA deshabilitado.
            LoginMfaRequiredDTO si MFA habilitado.

        Raises:
            UserNotFoundError: Teléfono no registrado.
            AccountLockedError: Cuenta bloqueada.
            InvalidCredentialsError: Contraseña incorrecta.
        """
        user = await self._user_repository.find_by_phone(input_dto.phone)

        if user is None:
            logger.info(
                '{"event":"login_failed","phone":"%s","reason":"user_not_found"}',
                input_dto.phone,
            )
            raise UserNotFoundError("Phone number not registered")

        if user.is_kyc_rejected():
            logger.info(
                '{"event":"login_failed","user_id":"%s","reason":"account_locked"}',
                user.id,
            )
            raise AccountLockedError("Account locked due to KYC rejection")

        if not self._password_hasher.verify_password(input_dto.password, user.password_hash):
            logger.info(
                '{"event":"login_failed","user_id":"%s","reason":"wrong_password"}',
                user.id,
            )
            raise InvalidCredentialsError("Invalid credentials")

        user_id = user.id or ""

        if user.mfa_enabled:
            temp_token = self._token_provider.generate_temp_token(user_id)
            logger.info(
                '{"event":"login_mfa_required","user_id":"%s"}',
                user_id,
            )
            await self._event_publisher.publish(
                "LoginMfaRequired",
                {"user_id": user_id, "phone": user.phone},
            )
            return LoginMfaRequiredDTO(temp_token=temp_token)

        access_token = self._token_provider.generate_access_token(user_id, user.phone)
        refresh_token = self._token_provider.generate_refresh_token(user_id)

        logger.info(
            '{"event":"login_success","user_id":"%s","ip":"127.0.0.1"}',
            user_id,
        )
        await self._event_publisher.publish(
            "LoginSuccess",
            {"user_id": user_id, "phone": user.phone, "ip": "127.0.0.1"},
        )

        return LoginOutputDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )
