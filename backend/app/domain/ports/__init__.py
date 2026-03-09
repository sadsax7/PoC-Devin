"""
Puertos del dominio — Interfaces (contratos) para adaptadores externos.

Define las abstracciones que el dominio necesita sin conocer implementaciones:
- UserRepository: persistencia de usuarios.
- KycVerificationPort: verificación de identidad.
- PasswordHasherPort: hashing de credenciales.
- TokenProviderPort: generación/validación de JWT.
- EventPublisherPort: publicación de eventos de dominio.

Referencia: BACKEND-GUIDELINES.md §2.1, §3.1
"""

from app.domain.ports.event_publisher_port import EventPublisherPort
from app.domain.ports.kyc_verification_port import KycVerificationPort
from app.domain.ports.mfa_verifier_port import MfaVerifierPort
from app.domain.ports.password_hasher_port import PasswordHasherPort
from app.domain.ports.token_provider_port import TokenProviderPort
from app.domain.ports.user_repository import UserRepository

__all__ = [
    "EventPublisherPort",
    "KycVerificationPort",
    "MfaVerifierPort",
    "PasswordHasherPort",
    "TokenProviderPort",
    "UserRepository",
]
