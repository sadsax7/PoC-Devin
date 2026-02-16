"""Puerto del hasher de contrasenas del dominio.

Define el contrato para servicios de hashing de contrasenas.
"""

from abc import ABC, abstractmethod


class PasswordHasherPort(ABC):
    """Puerto para hashing de contrasenas.

    Define la interfaz para generar hashes seguros de contrasenas.
    """

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Genera un hash seguro de la contrasena.

        Args:
            password: Contrasena en texto plano.

        Returns:
            Hash de la contrasena.
        """
