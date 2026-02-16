"""Contenedor de dependencias para inyeccion.

Proporciona las instancias de los adaptadores de salida
necesarios para los casos de uso. Usa singletons para
evitar instanciacion repetida de adaptadores sin estado.
"""

from functools import lru_cache

from app.adapters.outbound.db.mongo_client import get_database
from app.adapters.outbound.db.user_repository_impl import MongoUserRepository
from app.adapters.outbound.kyc.kyc_client_impl import MockKycClient
from app.adapters.outbound.security.password_hasher_impl import \
    Argon2PasswordHasher
from app.application.use_cases.register_user_use_case import \
    RegisterUserUseCase


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
