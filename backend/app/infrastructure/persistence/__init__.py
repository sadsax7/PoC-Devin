"""
Implementaciones de repositorios.
"""

from typing import List, Optional
from uuid import uuid4

from app.domain.entities.user import User
from app.domain.repositories import UserRepository


class InMemoryUserRepository(UserRepository):
    """Implementación en memoria del repositorio de usuarios."""

    def __init__(self) -> None:
        """Inicializa el repositorio."""
        self._users: dict[str, User] = {}

    async def create(self, user: User) -> User:
        """Crea un nuevo usuario."""
        user.id = str(uuid4())
        self._users[user.id] = user
        return user

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Busca un usuario por ID."""
        return self._users.get(user_id)

    async def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email."""
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def find_all(self) -> List[User]:
        """Obtiene todos los usuarios."""
        return list(self._users.values())

    async def update(self, user: User) -> User:
        """Actualiza un usuario."""
        if user.id and user.id in self._users:
            self._users[user.id] = user
            return user
        raise ValueError(f"Usuario con ID {user.id} no encontrado")

    async def delete(self, user_id: str) -> bool:
        """Elimina un usuario."""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
