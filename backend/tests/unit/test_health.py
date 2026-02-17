"""
Test de humo para verificar que el andamiaje base funciona.

Valida la configuración de Settings y la estructura del health check.
Patrón AAA obligatorio (BACKEND-GUIDELINES.md §5.4).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient


class TestSettings:
    """Tests unitarios para la configuración de la aplicación."""

    def test_settings_when_defaults_then_loads_correctly(self) -> None:
        """Verifica que Settings carga valores por defecto."""
        # Arrange & Act
        from app.config import Settings

        config = Settings()

        # Assert
        assert config.app_name == "Backend Hexagonal"
        assert config.app_version == "0.1.0"
        assert config.debug is True
        assert config.api_prefix == "/api/v1"

    def test_settings_when_mongodb_defaults_then_has_connection_string(self) -> None:
        """Verifica que Settings incluye config de MongoDB."""
        # Arrange & Act
        from app.config import Settings

        config = Settings()

        # Assert
        assert "mongodb://" in config.mongodb_uri
        assert config.mongodb_db_name == "billetera_db"

    def test_settings_when_jwt_defaults_then_has_key_paths(self) -> None:
        """Verifica que Settings incluye config de JWT."""
        # Arrange & Act
        from app.config import Settings

        config = Settings()

        # Assert
        assert config.jwt_private_key_path.endswith(".pem")
        assert config.jwt_public_key_path.endswith(".pem")
        assert config.jwt_access_token_expire_minutes == 15
        assert config.jwt_refresh_token_expire_days == 7

    def test_settings_when_kyc_defaults_then_mock_enabled(self) -> None:
        """Verifica que KYC mock está habilitado por defecto."""
        # Arrange & Act
        from app.config import Settings

        config = Settings()

        # Assert
        assert config.kyc_mock_enabled is True
        assert "kyc" in config.kyc_service_url


class TestHealthEndpoint:
    """Tests unitarios para el endpoint /health."""

    def test_health_check_when_db_connected_then_returns_ok(self) -> None:
        """Verifica que /health retorna status ok cuando MongoDB responde."""
        # Arrange
        mock_client = MagicMock()
        mock_client.admin.command = AsyncMock(return_value={"ok": 1})

        from main import app

        app.state.mongo_client = mock_client
        client = TestClient(app, raise_server_exceptions=False)

        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"
        assert data["version"] == "0.1.0"

    def test_health_check_when_db_disconnected_then_returns_disconnected(self) -> None:
        """Verifica que /health reporta DB disconnected cuando falla el ping."""
        # Arrange
        mock_client = MagicMock()
        mock_client.admin.command = AsyncMock(side_effect=Exception("Connection refused"))

        from main import app

        app.state.mongo_client = mock_client
        client = TestClient(app, raise_server_exceptions=False)

        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "disconnected"
