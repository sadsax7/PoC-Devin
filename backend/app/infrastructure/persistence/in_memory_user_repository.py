"""
Implementación en memoria del repositorio de usuarios.

Adaptador de persistencia para desarrollo y testing que almacena
los usuarios en un diccionario en memoria.
"""

from typing import List, Optional
from uuid import uuid4

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    """Implementación en memoria del repositorio de usuarios.

    Almacena usuarios en un diccionario interno. Útil para desarrollo
    y pruebas sin dependencias externas de base de datos.
    """

    def __init__(self) -> None:
        """Inicializa el repositorio con un almacén vacío."""
        self._users: dict[str, User] = {}

    async def create(self, user: User) -> User:
        """Crea un nuevo usuario asignándole un ID único.

        Args:
            user: Entidad User a persistir.

        Returns:
            User con identificador UUID asignado.
        """
        user.id = str(uuid4())
        self._users[user.id] = user
        return user

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Busca un usuario por ID.

        Args:
            user_id: Identificador único del usuario.

        Returns:
            User si existe, None en caso contrario.
        """
        return self._users.get(user_id)

    async def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email.

        Args:
            email: Correo electrónico del usuario.

        Returns:
            User si existe, None en caso contrario.
        """
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def find_all(self) -> List[User]:
        """Obtiene todos los usuarios.

        Returns:
            Lista de todos los usuarios almacenados.
        """
        return list(self._users.values())

    async def update(self, user: User) -> User:
        """Actualiza un usuario existente.

        Args:
            user: Entidad User con datos actualizados.

        Returns:
            User actualizado.

        Raises:
            ValueError: Si el usuario no existe en el almacén.
        """
        if user.id and user.id in self._users:
            self._users[user.id] = user
            return user
        raise ValueError(f"Usuario con ID {user.id} no encontrado")

    async def delete(self, user_id: str) -> bool:
        """Elimina un usuario por ID.

        Args:
            user_id: Identificador único del usuario a eliminar.

        Returns:
            True si se eliminó, False si no existía.
        """
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
