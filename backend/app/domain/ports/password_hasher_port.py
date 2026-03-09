"""
Puerto: PasswordHasherPort.

Abstracción para hashing de contraseñas.
Implementado por adapters/outbound/security/password_hasher_impl.py.

Referencia: BACKEND-GUIDELINES.md §2.1, HU-BE-01 AC#3
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class PasswordHasherPort(ABC):
    """Contrato para hashing/verificación de contraseñas."""

    @abstractmethod
    def hash_password(self, plain_password: str) -> str:
        """Genera hash de una contraseña en texto plano.

        Args:
            plain_password: Contraseña en texto plano.

        Returns:
            Hash Argon2 de la contraseña.
        """
        ...

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash.

        Args:
            plain_password: Contraseña en texto plano.
            hashed_password: Hash almacenado.

        Returns:
            True si la contraseña coincide con el hash.
        """
        ...
