"""
Tests unitarios para la fábrica de la aplicación FastAPI.
"""

from fastapi import FastAPI

from app.infrastructure.api.app import create_app


def test_create_app_returns_fastapi_instance() -> None:
    """Caso positivo: create_app retorna una instancia de FastAPI."""
    # Arrange & Act
    app = create_app()

    # Assert
    assert isinstance(app, FastAPI)


def test_create_app_has_correct_title() -> None:
    """Caso positivo: la app tiene el título configurado."""
    # Arrange & Act
    app = create_app()

    # Assert
    assert app.title == "Backend Hexagonal"


def test_create_app_includes_health_route() -> None:
    """Caso positivo: la app incluye la ruta /health."""
    # Arrange & Act
    app = create_app()

    # Assert
    routes = [getattr(route, "path", None) for route in app.routes]
    assert "/health" in routes
