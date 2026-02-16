"""Interfaces de repositorios del dominio.

Re-exporta los puertos de repositorio para acceso conveniente.
"""

from app.domain.ports.user_repository import UserRepositoryPort

__all__ = ["UserRepositoryPort"]
