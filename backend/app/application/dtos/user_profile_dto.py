"""DTOs para el caso de uso de perfil de usuario.

Define los objetos de transferencia de datos para la consulta
del perfil del usuario autenticado.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserProfileInputDTO:
    """DTO de entrada para consultar perfil de usuario.

    Attributes:
        user_id: Identificador unico del usuario autenticado.
    """

    user_id: str


@dataclass(frozen=True)
class UserProfileOutputDTO:
    """DTO de salida con datos sanitizados del perfil de usuario.

    Attributes:
        user_id: Identificador unico del usuario.
        phone: Numero de telefono en formato E.164.
        email: Correo electronico del usuario (opcional).
        name: Nombre del usuario (opcional).
        kyc_status: Estado de verificacion KYC.
        mfa_enabled: Indica si MFA esta habilitado.
        created_at: Fecha y hora de creacion en formato ISO 8601.
    """

    user_id: str
    phone: str
    email: Optional[str]
    name: Optional[str]
    kyc_status: str
    mfa_enabled: bool
    created_at: str
