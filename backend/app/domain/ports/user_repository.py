"""
Puerto: UserRepository.

Interfaz abstracta para persistencia de usuarios.
Implementado por adapters/outbound/db/user_repository_impl.py.

Referencia: BACKEND-GUIDELINES.md §2.1, §3.1, §5.1.3
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.user import User


class UserRepository(ABC):
    """Contrato de persistencia de usuarios.

    El dominio depende de esta interfaz; la implementación
    concreta (MongoDB/Motor) vive en adapters.
    """

    @abstractmethod
    async def save(self, user: User) -> str:
        """Persiste un usuario nuevo.

        Args:
            user: Entidad User a guardar.

        Returns:
            ID generado por la base de datos (string).
        """
        ...

    @abstractmethod
    async def find_by_phone(self, phone: str) -> User | None:
        """Busca un usuario por número de teléfono.

        Args:
            phone: Número E.164.

        Returns:
            User si existe, None en caso contrario.
        """
        ...

    @abstractmethod
    async def find_by_id(self, user_id: str) -> User | None:
        """Busca un usuario por ID.

        Args:
            user_id: Identificador único del usuario.

        Returns:
            User si existe, None en caso contrario.
        """
        ...

    @abstractmethod
    async def ensure_indexes(self) -> None:
        """Crea los índices necesarios en la colección.

        Debe crear un índice único sobre `phone`.
        """
        ...
