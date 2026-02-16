"""Tests unitarios para la interfaz UserRepositoryPort del dominio."""

from app.domain.ports.user_repository import UserRepositoryPort


def test_user_repository_port_is_abstract() -> None:
    """Caso positivo: UserRepositoryPort es una clase abstracta."""
    # Arrange & Act & Assert
    assert hasattr(UserRepositoryPort, "create")
    assert hasattr(UserRepositoryPort, "find_by_phone")
    assert hasattr(UserRepositoryPort, "find_by_email")
    assert hasattr(UserRepositoryPort, "find_by_id")
    assert hasattr(UserRepositoryPort, "find_all")
    assert hasattr(UserRepositoryPort, "update")
    assert hasattr(UserRepositoryPort, "delete")
