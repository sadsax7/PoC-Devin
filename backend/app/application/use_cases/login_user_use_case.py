"""Caso de uso para login de usuarios.

Orquesta el flujo de autenticacion: validacion de credenciales,
verificacion de estado KYC, y emision de tokens JWT.
"""

import logging

from app.application.dtos.login_user_dto import LoginUserInputDTO, LoginUserOutputDTO
from app.domain.ports.password_hasher_port import PasswordHasherPort
from app.domain.ports.token_provider_port import TokenProviderPort
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.services.authentication_service import (
    is_account_locked,
    requires_mfa,
    validate_login_password,
)
from app.shared.audit_logger import audit_log

logger = logging.getLogger(__name__)


class UserNotFoundError(Exception):
    """Error cuando el telefono no esta registrado."""


class InvalidCredentialsError(Exception):
    """Error cuando la contrasena es incorrecta."""


class AccountLockedError(Exception):
    """Error cuando la cuenta esta bloqueada por rechazo KYC."""


class LoginUserUseCase:
    """Caso de uso para autenticar un usuario existente.

    Coordina la validacion de credenciales, verificacion de estado
    de cuenta y emision de tokens JWT segun el flujo MFA.
    """

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        password_hasher: PasswordHasherPort,
        token_provider: TokenProviderPort,
    ) -> None:
        """Inicializa el caso de uso con sus dependencias.

        Args:
            user_repository: Puerto del repositorio de usuarios.
            password_hasher: Puerto del hasher de contrasenas.
            token_provider: Puerto del proveedor de tokens.
        """
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider

    async def execute(self, input_dto: LoginUserInputDTO) -> LoginUserOutputDTO:
        """Ejecuta el flujo de login de usuario.

        Args:
            input_dto: Datos de entrada del login.

        Returns:
            DTO con tokens o indicacion de MFA requerido.

        Raises:
            UserNotFoundError: Si el telefono no esta registrado.
            InvalidCredentialsError: Si la contrasena es incorrecta.
            AccountLockedError: Si la cuenta esta bloqueada.
        """
        if not validate_login_password(input_dto.password):
            audit_log(
                event="login_failed",
                phone=input_dto.phone,
                reason="invalid_password_format",
                ip="127.0.0.1",
            )
            raise InvalidCredentialsError("Invalid credentials")

        user = await self._user_repository.find_by_phone(input_dto.phone)
        if user is None:
            audit_log(
                event="login_failed",
                phone=input_dto.phone,
                reason="user_not_found",
                ip="127.0.0.1",
            )
            raise UserNotFoundError("Phone number not registered")

        if is_account_locked(user.kyc_status):
            audit_log(
                event="login_failed",
                user_id=user.id,
                phone=input_dto.phone,
                reason="account_locked",
                ip="127.0.0.1",
            )
            raise AccountLockedError("Account locked due to KYC rejection")

        if not self._password_hasher.verify_password(input_dto.password, user.password_hash):
            audit_log(
                event="login_failed",
                phone=input_dto.phone,
                reason="wrong_password",
                ip="127.0.0.1",
            )
            raise InvalidCredentialsError("Invalid credentials")

        if user.id is None:
            raise RuntimeError("User ID is missing")

        if requires_mfa(user.mfa_enabled):
            temp_token = self._token_provider.create_temp_token(user.id)
            audit_log(
                event="login_mfa_pending",
                user_id=user.id,
                ip="127.0.0.1",
            )
            return LoginUserOutputDTO(
                mfa_required=True,
                temp_token=temp_token,
                message="MFA verification required",
            )

        access_token = self._token_provider.create_access_token(user.id, user.phone)
        refresh_token = self._token_provider.create_refresh_token(user.id)
        audit_log(
            event="login_success",
            user_id=user.id,
            ip="127.0.0.1",
        )
        return LoginUserOutputDTO(
            mfa_required=False,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=1800,
        )
