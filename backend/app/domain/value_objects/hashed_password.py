"""
Value Object: HashedPassword.

Encapsula una contraseña hasheada. No almacena la contraseña en texto plano.
La validación de la contraseña plana se realiza como factory method.

Referencia: BACKEND-GUIDELINES.md §2.1, HU-BE-01 AC#2, AC#3
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_MIN_LENGTH = 8
_MAX_LENGTH = 128
_UPPERCASE_RE = re.compile(r"[A-Z]")
_LOWERCASE_RE = re.compile(r"[a-z]")
_DIGIT_RE = re.compile(r"\d")
_SPECIAL_RE = re.compile(r"[!@#$%^&*()_+\-=\[\]{}|;':\",./<>?\\`~]")


@dataclass(frozen=True, slots=True)
class HashedPassword:
    """Contraseña hasheada (inmutable).

    Attributes:
        value: Hash Argon2 de la contraseña.
    """

    value: str

    @staticmethod
    def validate_plain_password(password: str) -> list[str]:
        """Valida que una contraseña plana cumpla las reglas de negocio.

        Args:
            password: Contraseña en texto plano.

        Returns:
            Lista de errores de validación. Vacía si la contraseña es válida.
        """
        errors: list[str] = []

        if len(password) < _MIN_LENGTH:
            errors.append(f"Password must be at least {_MIN_LENGTH} characters")

        if len(password) > _MAX_LENGTH:
            errors.append(f"Password must be at most {_MAX_LENGTH} characters")

        if not _UPPERCASE_RE.search(password):
            errors.append("Password must contain at least one uppercase letter")

        if not _LOWERCASE_RE.search(password):
            errors.append("Password must contain at least one lowercase letter")

        if not _DIGIT_RE.search(password):
            errors.append("Password must contain at least one digit")

        if not _SPECIAL_RE.search(password):
            errors.append("Password must contain at least one special character")

        return errors
