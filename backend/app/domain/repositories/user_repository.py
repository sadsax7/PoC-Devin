"""
Interfaz del repositorio de usuarios.

Define el contrato que deben implementar los adaptadores de persistencia
para operaciones CRUD de la entidad User.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.user import User


class UserRepository(ABC):
    """Interfaz del repositorio de usuarios.

    Define las operaciones de persistencia disponibles para la entidad User.
    Las implementaciones concretas residen en la capa de infraestructura.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario.

        Args:
            user: Entidad User a persistir.

        Returns:
            User con identificador asignado.
        """

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Busca un usuario por ID.

        Args:
            user_id: Identificador único del usuario.

        Returns:
            User si existe, None en caso contrario.
        """

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email.

        Args:
            email: Correo electrónico del usuario.

        Returns:
            User si existe, None en caso contrario.
        """

    @abstractmethod
    async def find_all(self) -> List[User]:
        """Obtiene todos los usuarios.

        Returns:
            Lista de todos los usuarios persistidos.
        """

    @abstractmethod
    async def update(self, user: User) -> User:
        """Actualiza un usuario.

        Args:
            user: Entidad User con datos actualizados.

        Returns:
            User actualizado.
        """

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Elimina un usuario.

        Args:
            user_id: Identificador único del usuario a eliminar.

        Returns:
            True si se eliminó, False si no existía.
        """
