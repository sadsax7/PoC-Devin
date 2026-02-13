"""
Tests unitarios para la configuración de la aplicación.

Cubre casos positivos y edge cases de la clase Settings.
"""

from app.config.settings import Settings


def test_settings_default_values() -> None:
    """Caso positivo: Settings tiene valores por defecto correctos."""
    # Arrange & Act
    config = Settings(
        _env_file=None,  # type: ignore[call-arg]
    )

    # Assert
    assert config.app_name == "Backend Hexagonal"
    assert config.app_version == "0.1.0"
    assert config.debug is True
    assert config.api_prefix == "/api/v1"
    assert config.mongodb_uri == "mongodb://localhost:27017"
    assert config.mongodb_database == "billetera_virtual"


def test_settings_custom_values() -> None:
    """Caso positivo: Settings acepta valores personalizados."""
    # Arrange & Act
    config = Settings(
        app_name="Custom App",
        app_version="2.0.0",
        debug=False,
        api_prefix="/api/v2",
        mongodb_uri="mongodb://remotehost:27017",
        mongodb_database="custom_db",
        _env_file=None,  # type: ignore[call-arg]
    )

    # Assert
    assert config.app_name == "Custom App"
    assert config.app_version == "2.0.0"
    assert config.debug is False
    assert config.api_prefix == "/api/v2"
    assert config.mongodb_uri == "mongodb://remotehost:27017"
    assert config.mongodb_database == "custom_db"


def test_settings_mongodb_uri_is_string() -> None:
    """Edge case: mongodb_uri siempre es un string."""
    # Arrange & Act
    config = Settings(
        _env_file=None,  # type: ignore[call-arg]
    )

    # Assert
    assert isinstance(config.mongodb_uri, str)
    assert config.mongodb_uri.startswith("mongodb://")


def test_settings_singleton_import() -> None:
    """Caso positivo: el módulo exporta una instancia settings."""
    # Arrange & Act
    from app.config.settings import settings

    # Assert
    assert isinstance(settings, Settings)
