"""Implementacion del hasher de contrasenas con Argon2.

Adaptador de salida que implementa el puerto PasswordHasherPort
usando la libreria argon2-cffi.
"""

from argon2 import PasswordHasher

from app.domain.ports.password_hasher_port import PasswordHasherPort


class Argon2PasswordHasher(PasswordHasherPort):
    """Implementacion de hashing de contrasenas con Argon2.

    Utiliza argon2-cffi para generar hashes seguros.
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
