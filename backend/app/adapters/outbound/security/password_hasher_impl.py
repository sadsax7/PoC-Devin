"""Implementacion del hasher de contrasenas con Argon2.

Adaptador de salida que implementa el puerto PasswordHasherPort
usando la libreria argon2-cffi.
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

from app.domain.ports.password_hasher_port import PasswordHasherPort


class Argon2PasswordHasher(PasswordHasherPort):
    """Implementacion de hashing y verificacion de contrasenas con Argon2.

    Utiliza argon2-cffi para generar y verificar hashes seguros.
    """

    def __init__(self) -> None:
        """Inicializa el hasher con configuracion por defecto de Argon2."""
        self._hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Genera un hash Argon2 de la contrasena.

        Args:
            password: Contrasena en texto plano.

        Returns:
            Hash Argon2 de la contrasena.
        """
        return self._hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica una contrasena contra su hash Argon2 almacenado.

        Args:
            password: Contrasena en texto plano a verificar.
            password_hash: Hash Argon2 almacenado para comparar.

        Returns:
            True si la contrasena coincide con el hash.
        """
        try:
            return bool(self._hasher.verify(password_hash, password))
        except (VerifyMismatchError, VerificationError):
            return False
