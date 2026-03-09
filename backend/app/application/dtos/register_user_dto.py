"""
DTOs para el caso de uso de registro de usuarios.

Define los contratos de entrada y salida del RegisterUserUseCase.

Referencia: BACKEND-GUIDELINES.md §2.2, HU-BE-01 AC#7
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegisterUserInputDTO:
    """Datos de entrada para registrar un usuario.

    Attributes:
        phone: Número de teléfono E.164 (requerido).
        password: Contraseña en texto plano (requerido).
        email: Correo electrónico (opcional).
        name: Nombre del usuario (opcional).
    """

    phone: str
    password: str
    email: str | None = None
    name: str | None = None


@dataclass(frozen=True, slots=True)
class RegisterUserOutputDTO:
    """Resultado del registro exitoso.

    Attributes:
        user_id: ID generado para el usuario.
    """

    user_id: str
