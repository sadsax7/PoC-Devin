"""DTOs para el caso de uso de registro de usuarios.

Define las estructuras de datos de entrada y salida
para el flujo de registro.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RegisterUserInputDTO:
    """DTO de entrada para registrar un usuario.

    Attributes:
        phone: Numero de telefono en formato E.164.
        password: Contrasena en texto plano (sera hasheada).
        email: Correo electronico (opcional).
        name: Nombre del usuario (opcional).
    """

    phone: str
    password: str
    email: Optional[str] = None
    name: Optional[str] = None


@dataclass(frozen=True)
class RegisterUserOutputDTO:
    """DTO de salida del registro de usuario.

    Attributes:
        user_id: Identificador unico del usuario creado.
    """

    user_id: str
