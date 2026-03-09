"""
Wiring de dependencias (Dependency Injection Container).

Crea y provee las instancias de puertos y casos de uso
vinculadas a la DB de la request actual.

Referencia: BACKEND-GUIDELINES.md §2.3
"""

from __future__ import annotations

from fastapi import Depends, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.adapters.outbound.db.user_repository_impl import UserRepositoryImpl
from app.adapters.outbound.kyc.kyc_client_impl import KycClientMock
from app.adapters.outbound.messaging.event_publisher_memory import InMemoryEventPublisher
from app.adapters.outbound.security.password_hasher_impl import PasswordHasherImpl
from app.application.use_cases.register_user import RegisterUserUseCase
from app.domain.ports.event_publisher_port import EventPublisherPort
from app.domain.ports.kyc_verification_port import KycVerificationPort
from app.domain.ports.password_hasher_port import PasswordHasherPort
from app.domain.ports.user_repository import UserRepository


def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Obtiene la instancia de DB desde el estado de la app.

    Args:
        request: Request de FastAPI con acceso al state.

    Returns:
        Base de datos Motor async.
    """
    return request.app.state.db  # type: ignore[no-any-return]


def get_user_repository(
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UserRepository:
    """Provee la implementación del UserRepository.

    Args:
        db: Base de datos Motor inyectada.

    Returns:
        UserRepositoryImpl conectado a la DB.
    """
    return UserRepositoryImpl(db)


def get_password_hasher() -> PasswordHasherPort:
    """Provee la implementación del PasswordHasher.

    Returns:
        PasswordHasherImpl (Argon2).
    """
    return PasswordHasherImpl()


def get_kyc_verification() -> KycVerificationPort:
    """Provee la implementación del servicio KYC.

    Returns:
        KycClientMock para el PoC.
    """
    return KycClientMock()


def get_event_publisher() -> EventPublisherPort:
    """Provee la implementación del EventPublisher.

    Returns:
        InMemoryEventPublisher para el PoC.
    """
    return InMemoryEventPublisher()


def get_register_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasherPort = Depends(get_password_hasher),
    kyc_verification: KycVerificationPort = Depends(get_kyc_verification),
    event_publisher: EventPublisherPort = Depends(get_event_publisher),
) -> RegisterUserUseCase:
    """Provee el caso de uso RegisterUser con todas sus dependencias.

    Args:
        user_repository: Puerto de persistencia.
        password_hasher: Puerto de hashing.
        kyc_verification: Puerto de KYC.
        event_publisher: Puerto de eventos.

    Returns:
        RegisterUserUseCase completamente inyectado.
    """
    return RegisterUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        kyc_verification=kyc_verification,
        event_publisher=event_publisher,
    )
