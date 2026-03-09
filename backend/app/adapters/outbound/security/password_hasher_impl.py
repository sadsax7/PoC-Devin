"""
Adapter: PasswordHasherImpl (Argon2).

Implementación del puerto PasswordHasherPort usando argon2-cffi.

Referencia: BACKEND-GUIDELINES.md §2.4, §3.6, HU-BE-01 AC#3
"""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.domain.ports.password_hasher_port import PasswordHasherPort


class PasswordHasherImpl(PasswordHasherPort):
    """Implementación Argon2 del hasher de contraseñas."""

    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash_password(self, plain_password: str) -> str:
        """Genera hash Argon2id de una contraseña.

        Args:
            plain_password: Contraseña en texto plano.

        Returns:
            Hash Argon2id.
        """
        return self._hasher.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash Argon2.

        Args:
            plain_password: Contraseña en texto plano.
            hashed_password: Hash almacenado.

        Returns:
            True si la contraseña coincide.
        """
        try:
            return self._hasher.verify(hashed_password, plain_password)
        except VerifyMismatchError:
            return False
