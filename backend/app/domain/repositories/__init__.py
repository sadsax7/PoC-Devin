"""
Interfaces de repositorios del dominio.

Re-exporta los puertos de repositorio para acceso conveniente.
"""

from app.domain.repositories.user_repository import UserRepository

__all__ = ["UserRepository"]
