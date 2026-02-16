"""Puerto del hasher de contrasenas del dominio.

Define el contrato para servicios de hashing y verificacion de contrasenas.
"""

from abc import ABC, abstractmethod


class PasswordHasherPort(ABC):
    """Puerto para hashing y verificacion de contrasenas.

    Define la interfaz para generar y verificar hashes seguros de contrasenas.
    """

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Genera un hash seguro de la contrasena.

        Args:
            password: Contrasena en texto plano.

        Returns:
            Hash de la contrasena.
        """

    @abstractmethod
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica una contrasena contra su hash almacenado.

        Args:
            password: Contrasena en texto plano a verificar.
            password_hash: Hash almacenado para comparar.

        Returns:
            True si la contrasena coincide con el hash.
        """
