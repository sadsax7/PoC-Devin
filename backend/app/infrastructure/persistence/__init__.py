"""
Implementaciones de repositorios.

Re-exporta las implementaciones de repositorios para acceso conveniente.
"""

from app.infrastructure.persistence.in_memory_user_repository import \
    InMemoryUserRepository

__all__ = ["InMemoryUserRepository"]
