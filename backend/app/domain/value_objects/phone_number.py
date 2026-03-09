"""
Value Object: PhoneNumber.

Encapsula un número de teléfono en formato E.164 internacional.
Inmutable, validado en construcción.

Referencia: BACKEND-GUIDELINES.md §2.1, HU-BE-01 AC#1
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_E164_REGEX = re.compile(r"^\+[1-9]\d{6,14}$")


@dataclass(frozen=True, slots=True)
class PhoneNumber:
    """Número de teléfono en formato E.164.

    Attributes:
        value: Cadena E.164 validada (ej: +573001234567).
    """

    value: str

    def __post_init__(self) -> None:
        """Valida formato E.164 al construir.

        Raises:
            ValueError: Si el valor no cumple el formato E.164.
        """
        if not _E164_REGEX.match(self.value):
            raise ValueError(
                f"Phone number must be in E.164 format (e.g. +573001234567), got: {self.value}"
            )

    def ends_with(self, suffix: str) -> bool:
        """Verifica si el número termina con un sufijo dado.

        Args:
            suffix: Sufijo a verificar.

        Returns:
            True si el número termina con el sufijo.
        """
        return self.value.endswith(suffix)
