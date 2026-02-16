"""Puerto del repositorio de usuarios para el dominio.

Define el contrato que deben implementar los adaptadores de persistencia
para operaciones relacionadas con el registro de usuarios.
"""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities.user import User


class UserRepositoryPort(ABC):
    """Puerto del repositorio de usuarios.

    Define las operaciones de persistencia necesarias para
    el flujo de registro de usuarios.
    """

    @abstractmethod
    async def find_by_phone(self, phone: str) -> Optional[User]:
        """Busca un usuario por numero de telefono.

        Args:
            phone: Numero de telefono en formato E.164.

        Returns:
            User si existe, None en caso contrario.
        """

    @abstractmethod
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario.

        Args:
            user: Entidad User a persistir.

        Returns:
            User con identificador asignado.
        """
