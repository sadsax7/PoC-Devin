"""Tests para el puerto TokenProviderPort."""

from unittest.mock import MagicMock

from app.domain.ports.token_provider_port import TokenProviderPort


def test_token_provider_port_when_subclass_then_implements_interface() -> None:
    """Caso positivo: subclase implementa la interfaz correctamente."""

    class FakeTokenProvider(TokenProviderPort):
        def create_access_token(self, user_id: str, phone: str) -> str:
            return "access_token"

        def create_refresh_token(self, user_id: str) -> str:
            return "refresh_token"

        def create_temp_token(self, user_id: str) -> str:
            return "temp_token"

        def decode_token(self, token: str) -> dict[str, object]:
            return {"sub": "fake_id"}

    provider = FakeTokenProvider()
    assert provider.create_access_token("1", "+573001234567") == "access_token"
    assert provider.create_refresh_token("1") == "refresh_token"
    assert provider.create_temp_token("1") == "temp_token"


def test_token_provider_port_when_mock_then_callable() -> None:
    """Caso positivo: mock del puerto funciona correctamente."""
    mock_provider = MagicMock(spec=TokenProviderPort)
    mock_provider.create_access_token.return_value = "mocked_token"
    assert mock_provider.create_access_token("1", "+573001234567") == "mocked_token"


def test_token_provider_port_decode_when_mock_then_returns_claims() -> None:
    """Caso positivo: mock de decode retorna claims."""
    mock_provider = MagicMock(spec=TokenProviderPort)
    mock_provider.decode_token.return_value = {"sub": "123", "type": "access"}
    result = mock_provider.decode_token("some.token")
    assert result["sub"] == "123"
    assert result["type"] == "access"
