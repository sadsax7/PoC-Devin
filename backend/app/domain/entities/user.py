"""Entidad de usuario del dominio.

Representa un usuario del sistema con identidad unica,
incluyendo datos de autenticacion, KYC y MFA.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class User:
    """Entidad de usuario con identidad unica.

    Attributes:
        id: Identificador unico del usuario.
        phone: Numero de telefono en formato E.164.
        email: Correo electronico del usuario (opcional).
        name: Nombre del usuario (opcional).
        password_hash: Hash de la contrasena del usuario.
        kyc_status: Estado de verificacion KYC.
        mfa_enabled: Indica si MFA esta habilitado.
        created_at: Fecha y hora de creacion del usuario.
    """

    phone: str
    password_hash: str = ""
    email: Optional[str] = None
    name: Optional[str] = None
    kyc_status: str = "pending"
    mfa_enabled: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: Optional[str] = field(default=None)
