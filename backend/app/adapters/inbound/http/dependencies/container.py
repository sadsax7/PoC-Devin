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
from app.adapters.outbound.security.mfa_verifier_impl import MfaVerifierImpl
from app.adapters.outbound.security.password_hasher_impl import PasswordHasherImpl
from app.adapters.outbound.security.token_provider_impl import TokenProviderImpl
from app.application.use_cases.login_user import LoginUserUseCase
from app.application.use_cases.register_user import RegisterUserUseCase
from app.application.use_cases.verify_mfa import VerifyMfaUseCase
from app.config import settings
from app.domain.ports.event_publisher_port import EventPublisherPort
from app.domain.ports.kyc_verification_port import KycVerificationPort
from app.domain.ports.mfa_verifier_port import MfaVerifierPort
from app.domain.ports.password_hasher_port import PasswordHasherPort
from app.domain.ports.token_provider_port import TokenProviderPort
from app.domain.ports.user_repository import UserRepository
from app.domain.services.mfa_attempt_tracker import MfaAttemptTracker

# ── Singletons ────────────────────────────────────────────────
_mfa_attempt_tracker = MfaAttemptTracker()


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


def get_token_provider() -> TokenProviderPort:
    """Provee la implementación del TokenProvider (JWT RS256).

    Returns:
        TokenProviderImpl con claves RSA desde settings.
    """
    return TokenProviderImpl(
        private_key_path=settings.jwt_private_key_path,
        public_key_path=settings.jwt_public_key_path,
        access_expire=settings.jwt_access_token_expire_minutes * 60,
        refresh_expire=settings.jwt_refresh_token_expire_days * 86400,
        temp_expire=settings.jwt_temp_token_expire_minutes * 60,
    )


def get_mfa_verifier() -> MfaVerifierPort:
    """Provee la implementación del verificador MFA.

    Returns:
        MfaVerifierImpl (mock con código "123456").
    """
    return MfaVerifierImpl()


def get_mfa_attempt_tracker() -> MfaAttemptTracker:
    """Provee la instancia singleton de MfaAttemptTracker.

    Returns:
        MfaAttemptTracker compartido entre requests.
    """
    return _mfa_attempt_tracker


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


def get_login_user_use_case(
    user_repository: UserRepository = Depends(get_user_repository),
    password_hasher: PasswordHasherPort = Depends(get_password_hasher),
    token_provider: TokenProviderPort = Depends(get_token_provider),
    event_publisher: EventPublisherPort = Depends(get_event_publisher),
) -> LoginUserUseCase:
    """Provee el caso de uso LoginUser con todas sus dependencias.

    Args:
        user_repository: Puerto de persistencia.
        password_hasher: Puerto de hashing.
        token_provider: Puerto de tokens JWT.
        event_publisher: Puerto de eventos.

    Returns:
        LoginUserUseCase completamente inyectado.
    """
    return LoginUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_provider=token_provider,
        event_publisher=event_publisher,
    )


def get_verify_mfa_use_case(
    token_provider: TokenProviderPort = Depends(get_token_provider),
    mfa_verifier: MfaVerifierPort = Depends(get_mfa_verifier),
    user_repository: UserRepository = Depends(get_user_repository),
    event_publisher: EventPublisherPort = Depends(get_event_publisher),
    attempt_tracker: MfaAttemptTracker = Depends(get_mfa_attempt_tracker),
) -> VerifyMfaUseCase:
    """Provee el caso de uso VerifyMfa con todas sus dependencias.

    Args:
        token_provider: Puerto de tokens JWT.
        mfa_verifier: Puerto de verificación MFA.
        user_repository: Puerto de persistencia.
        event_publisher: Puerto de eventos.
        attempt_tracker: Rastreador de intentos MFA.

    Returns:
        VerifyMfaUseCase completamente inyectado.
    """
    return VerifyMfaUseCase(
        token_provider=token_provider,
        mfa_verifier=mfa_verifier,
        user_repository=user_repository,
        event_publisher=event_publisher,
        attempt_tracker=attempt_tracker,
    )
