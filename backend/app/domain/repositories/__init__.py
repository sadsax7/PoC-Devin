"""
Interfaces de repositorios del dominio.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.user import User


class UserRepository(ABC):
    """Interfaz del repositorio de usuarios."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Crea un nuevo usuario."""
        pass

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Busca un usuario por ID."""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Busca un usuario por email."""
        pass

    @abstractmethod
    async def find_all(self) -> List[User]:
        """Obtiene todos los usuarios."""
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        """Actualiza un usuario."""
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Elimina un usuario."""
        pass
