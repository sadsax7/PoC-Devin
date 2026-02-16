"""Contenedor de dependencias para inyeccion.

Proporciona las instancias de los adaptadores de salida
necesarios para los casos de uso.
"""

from app.adapters.outbound.db.mongo_client import get_database
from app.adapters.outbound.db.user_repository_impl import MongoUserRepository
from app.adapters.outbound.kyc.kyc_client_impl import MockKycClient
from app.adapters.outbound.security.password_hasher_impl import \
    Argon2PasswordHasher
from app.application.use_cases.register_user_use_case import \
    RegisterUserUseCase


def get_register_user_use_case() -> RegisterUserUseCase:
    """Crea una instancia del caso de uso de registro con sus dependencias.

    Returns:
        Instancia configurada de RegisterUserUseCase.
    """
    database = get_database()
    user_repository = MongoUserRepository(database)
    kyc_client = MockKycClient()
    password_hasher = Argon2PasswordHasher()
    return RegisterUserUseCase(
        user_repository=user_repository,
        kyc_verification=kyc_client,
        password_hasher=password_hasher,
    )
