"""
Tests unitarios para la interfaz UserRepository del dominio.
"""

from app.domain.repositories import UserRepository


def test_user_repository_is_abstract() -> None:
    """Caso positivo: UserRepository es una clase abstracta."""
    # Arrange & Act & Assert
    assert hasattr(UserRepository, "create")
    assert hasattr(UserRepository, "find_by_id")
    assert hasattr(UserRepository, "find_by_email")
    assert hasattr(UserRepository, "find_all")
    assert hasattr(UserRepository, "update")
    assert hasattr(UserRepository, "delete")
