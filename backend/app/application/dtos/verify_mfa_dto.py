"""DTOs para el caso de uso de verificacion MFA.

Define las estructuras de datos de entrada y salida
para el flujo de verificacion de codigo MFA.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class VerifyMfaInputDTO:
    """DTO de entrada para verificacion MFA.

    Attributes:
        temp_token: Token temporal JWT del login con MFA pendiente.
        code: Codigo de verificacion de 6 digitos.
    """

    temp_token: str
    code: str


@dataclass(frozen=True)
class VerifyMfaOutputDTO:
    """DTO de salida de verificacion MFA exitosa.

    Attributes:
        access_token: Token JWT de acceso.
        refresh_token: Token JWT de renovacion.
        token_type: Tipo de token (Bearer).
        expires_in: Tiempo de expiracion en segundos.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 1800
