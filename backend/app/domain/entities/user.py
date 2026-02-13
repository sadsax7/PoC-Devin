"""
Entidad de usuario del dominio.

Representa un usuario del sistema con identidad única.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class User:
    """Entidad de usuario con identidad única.

    Attributes:
        id: Identificador único del usuario.
        email: Correo electrónico del usuario.
        password_hash: Hash de la contraseña del usuario.
        full_name: Nombre completo del usuario.
        is_active: Indica si el usuario está activo.
    """

    email: str
    password_hash: str = ""
    full_name: str = ""
    is_active: bool = True
    id: Optional[str] = field(default=None)
