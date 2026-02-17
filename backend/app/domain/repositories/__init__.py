"""
Interfaces de repositorios del dominio.

Nota: En la arquitectura hexagonal, los repositorios son ports del dominio.
Definidos aquí como contratos abstractos implementados por adapters/outbound/db.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class UserRepository(ABC):
    """Interfaz del repositorio de usuarios.

    Define las operaciones de persistencia disponibles sin
    acoplar el dominio a ninguna base de datos concreta.
    """

    @abstractmethod
    async def create(self, user: object) -> object:
        """Crea un nuevo usuario."""
        ...

    @abstractmethod
    async def find_by_id(self, user_id: str) -> object | None:
        """Busca un usuario por ID."""
        ...

    @abstractmethod
    async def find_by_email(self, email: str) -> object | None:
        """Busca un usuario por email."""
        ...

    @abstractmethod
    async def find_all(self) -> list[object]:
        """Obtiene todos los usuarios."""
        ...

    @abstractmethod
    async def update(self, user: object) -> object:
        """Actualiza un usuario."""
        ...

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Elimina un usuario."""
        ...
