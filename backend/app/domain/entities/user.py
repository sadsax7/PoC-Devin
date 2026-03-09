"""
Entidad de dominio: User.

Representa un usuario del sistema con identidad,
credenciales y estado de KYC.

Referencia: BACKEND-GUIDELINES.md §2.1, HU-BE-01 AC#1
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class KycStatus(str, Enum):
    """Estados posibles de verificación KYC.

    Values:
        PENDING: Verificación en curso.
        APPROVED: Verificación aprobada.
        REJECTED: Verificación rechazada.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(slots=True)
class User:
    """Entidad de dominio User.

    Attributes:
        id: Identificador único (ObjectId como string).
        phone: Número de teléfono E.164.
        email: Correo electrónico opcional.
        name: Nombre del usuario opcional.
        password_hash: Hash Argon2 de la contraseña.
        kyc_status: Estado actual de verificación KYC.
        mfa_enabled: Indica si MFA está activado.
        created_at: Fecha/hora de creación UTC.
    """

    phone: str
    password_hash: str
    kyc_status: KycStatus = KycStatus.PENDING
    id: str | None = None
    email: str | None = None
    name: str | None = None
    mfa_enabled: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def is_kyc_rejected(self) -> bool:
        """Indica si el usuario fue rechazado por KYC.

        Returns:
            True si kyc_status es REJECTED.
        """
        return self.kyc_status == KycStatus.REJECTED

    def to_dict(self) -> dict[str, object]:
        """Convierte la entidad a diccionario para persistencia.

        Returns:
            Diccionario con todos los campos del usuario.
            Excluye el campo 'id' (lo asigna MongoDB).
        """
        data: dict[str, object] = {
            "phone": self.phone,
            "password_hash": self.password_hash,
            "kyc_status": self.kyc_status.value,
            "mfa_enabled": self.mfa_enabled,
            "created_at": self.created_at,
        }
        if self.email is not None:
            data["email"] = self.email
        if self.name is not None:
            data["name"] = self.name
        return data
