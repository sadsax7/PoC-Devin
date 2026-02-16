"""Servicio de dominio para registro de usuarios.

Contiene la logica de negocio pura para el proceso de registro,
incluyendo validacion de contrasena y coordinacion de KYC.
"""

import re
from typing import Optional

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_MAX_LENGTH = 128
_EMAIL_MAX_LENGTH = 255
_NAME_MAX_LENGTH = 100


def validate_password(password: str) -> Optional[str]:
    """Valida que la contrasena cumpla con las reglas de seguridad.

    Reglas:
        - Minimo 8 caracteres, maximo 128 caracteres.
        - Al menos una letra mayuscula.
        - Al menos una letra minuscula.
        - Al menos un numero.
        - Al menos un caracter especial.

    Args:
        password: Contrasena a validar.

    Returns:
        Mensaje de error si no cumple, None si es valida.
    """
    if len(password) < _PASSWORD_MIN_LENGTH:
        return f"Password must be at least {_PASSWORD_MIN_LENGTH} characters"
    if len(password) > _PASSWORD_MAX_LENGTH:
        return f"Password must be at most {_PASSWORD_MAX_LENGTH} characters"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one digit"
    if not re.search(r"[^A-Za-z0-9]", password):
        return "Password must contain at least one special character"
    return None


def validate_email(email: str) -> Optional[str]:
    """Valida el formato y longitud del email.

    Args:
        email: Correo electronico a validar.

    Returns:
        Mensaje de error si no cumple, None si es valido.
    """
    if len(email) > _EMAIL_MAX_LENGTH:
        return f"Email must be at most {_EMAIL_MAX_LENGTH} characters"
    email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    if not email_pattern.match(email):
        return "Invalid email format"
    return None


def validate_name(name: str) -> Optional[str]:
    """Valida la longitud del nombre.

    Args:
        name: Nombre a validar.

    Returns:
        Mensaje de error si no cumple, None si es valido.
    """
    if len(name) > _NAME_MAX_LENGTH:
        return f"Name must be at most {_NAME_MAX_LENGTH} characters"
    return None
