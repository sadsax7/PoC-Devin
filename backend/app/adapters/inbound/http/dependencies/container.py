"""Contenedor de dependencias para inyeccion.

Proporciona las instancias de los adaptadores de salida
necesarios para los casos de uso. Usa singletons para
evitar instanciacion repetida de adaptadores sin estado.
"""

from functools import lru_cache

from app.adapters.outbound.db.mongo_client import get_database
from app.adapters.outbound.db.user_repository_impl import MongoUserRepository
from app.adapters.outbound.kyc.kyc_client_impl import MockKycClient
from app.adapters.outbound.security.password_hasher_impl import Argon2PasswordHasher
from app.adapters.outbound.security.token_provider_impl import JwtTokenProvider
from app.application.use_cases.get_user_profile_use_case import GetUserProfileUseCase
from app.application.use_cases.login_user_use_case import LoginUserUseCase
from app.application.use_cases.register_user_use_case import RegisterUserUseCase
from app.application.use_cases.verify_mfa_use_case import MfaRateLimiter, VerifyMfaUseCase
from app.config.settings import settings


@lru_cache(maxsize=1)
def _get_password_hasher() -> Argon2PasswordHasher:
    """Retorna instancia singleton del hasher de contrasenas.

    Returns:
        Instancia unica de Argon2PasswordHasher.
    """
    return Argon2PasswordHasher()


@lru_cache(maxsize=1)
def _get_kyc_client() -> MockKycClient:
    """Retorna instancia singleton del cliente KYC mock.

    Returns:
        Instancia unica de MockKycClient.
    """
    return MockKycClient()


@lru_cache(maxsize=1)
def _get_token_provider() -> JwtTokenProvider:
    """Retorna instancia singleton del proveedor de tokens JWT.

    Returns:
        Instancia unica de JwtTokenProvider con claves RS256.
    """
    private_key = settings.jwt_private_key.replace("\\n", "\n")
    public_key = settings.jwt_public_key.replace("\\n", "\n")
    return JwtTokenProvider(private_key=private_key, public_key=public_key)


@lru_cache(maxsize=1)
def _get_mfa_rate_limiter() -> MfaRateLimiter:
    """Retorna instancia singleton del limitador de intentos MFA.

    Returns:
        Instancia unica de MfaRateLimiter.
    """
    return MfaRateLimiter()


def get_register_user_use_case() -> RegisterUserUseCase:
    """Crea una instancia del caso de uso de registro con sus dependencias.

    Returns:
        Instancia configurada de RegisterUserUseCase.
    """
    database = get_database()
    user_repository = MongoUserRepository(database)
    return RegisterUserUseCase(
        user_repository=user_repository,
        kyc_verification=_get_kyc_client(),
        password_hasher=_get_password_hasher(),
    )


def get_login_user_use_case() -> LoginUserUseCase:
    """Crea una instancia del caso de uso de login con sus dependencias.

    Returns:
        Instancia configurada de LoginUserUseCase.
    """
    database = get_database()
    user_repository = MongoUserRepository(database)
    return LoginUserUseCase(
        user_repository=user_repository,
        password_hasher=_get_password_hasher(),
        token_provider=_get_token_provider(),
    )


def get_verify_mfa_use_case() -> VerifyMfaUseCase:
    """Crea una instancia del caso de uso de verificacion MFA con sus dependencias.

    Returns:
        Instancia configurada de VerifyMfaUseCase.
    """
    database = get_database()
    user_repository = MongoUserRepository(database)
    return VerifyMfaUseCase(
        user_repository=user_repository,
        token_provider=_get_token_provider(),
        rate_limiter=_get_mfa_rate_limiter(),
    )


def get_user_profile_use_case() -> GetUserProfileUseCase:
    """Crea una instancia del caso de uso de perfil de usuario con sus dependencias.

    Returns:
        Instancia configurada de GetUserProfileUseCase.
    """
    database = get_database()
    user_repository = MongoUserRepository(database)
    return GetUserProfileUseCase(user_repository=user_repository)
