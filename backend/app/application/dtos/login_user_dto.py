"""DTOs para el caso de uso de login de usuarios.

Define las estructuras de datos de entrada y salida
para el flujo de autenticacion.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LoginUserInputDTO:
    """DTO de entrada para login de usuario.

    Attributes:
        phone: Numero de telefono en formato E.164.
        password: Contrasena en texto plano.
    """

    phone: str
    password: str


@dataclass(frozen=True)
class LoginUserOutputDTO:
    """DTO de salida del login de usuario.

    Attributes:
        access_token: Token JWT de acceso (None si MFA requerido).
        refresh_token: Token JWT de renovacion (None si MFA requerido).
        temp_token: Token temporal para MFA (None si MFA no requerido).
        mfa_required: Indica si se requiere verificacion MFA.
        token_type: Tipo de token (Bearer).
        expires_in: Tiempo de expiracion en segundos.
        message: Mensaje informativo (opcional).
    """

    mfa_required: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    temp_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int = 1800
    message: Optional[str] = None
