"""Tests para la implementacion del proveedor de tokens JWT."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.adapters.outbound.security.token_provider_impl import JwtTokenProvider
from app.domain.ports.token_provider_port import (
    TokenExpiredException,
    TokenInvalidException,
)

_TEST_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDOEdOlTaEKdCEp
IKGH2QX4XH0bwjcklBYbiLRGzOPSLU7fx5HWU3oKdundcrUr25Aq+9M4ECq0IPQm
ySpcSOJoi4l4gYTlqUFGoAUA9Cux08xlyawvSB+3cg+gwbxUZWKMUIkierfmU1X+
xIW0Yirdv5wGqxxBu7T7mZhQU7l4PxnEv1S9fEKoR77cOz6k/tOsrXRuhvj0MQIK
/WuPpITyjkABDePAg7k2loCAxJA1ARAcrvx/+1xsbyRInyLmVhkhFcfUwcrs8oYj
3qZ6W94a4lY5aSZqHmGCHRbkCybt3zONRFb4xZ9ESHpL2dvj2KNJt7y/AGCEhLdD
YdpppjffAgMBAAECggEAEW45mFBuMEutaGSttSd61UzBemEdt/bcvdx830ZCeQtD
EjO31si92HfBhW1H/Ns4ISKm9aWMbysga811S1QQ7qXq7WoLOz/rWRV9Bt0gewy+
y9dYvLEdma9IuiDZFMx0nwjK6MM3ngBrlD68TotFM/eas4eyvq6peuS9mQHT/OM2
i6n12PHFIWrqhmSGOg8FAKQSEv8i3WC/V0/26vGPSPwBNjZtSJN6ZGv4ea9CdamV
U0NBbx417GEfWjzJEmOmgc2hc9jhYBnmcCkB5Q6jlDmAoi4tgCaVCgsrduMNumoE
xDKrSdgR5NHWg021kIey9HBAV7h/oRd6zx+RiGpYaQKBgQD3tki6WrBckfTKPyXH
SLbdXN1we8MWBFF+hKjJts6Byd8VwaHS328ERKDrvmMy8vorSBltq88/MfPkZiMA
vejCs/e2tovwlrnHhrOBU36lBdf5Jj7e8U47O5aRtDGro7frvrp+zcvCMrkrbT0L
fh7xFyN1BuLHALTn2s7lwy+yJwKBgQDU9t1sO7MSzdeQjMerkDjzZR8Q5hQ5LYql
w7x1Mess5189ucsU9034w/JyEh9pi6LeO9bk0nrlTNAYUJJ4ahuyHoMqqBy4dueO
1nUleNsF67qAXwZdn43xADTZpdy7Y6gXg+/zETbJkAN7bUyU/6HAmXWOrSe4VgTg
Npzapsq3iQKBgQDo3npchmkJfUTs5JR1Vgxi6axa1F4/0mtyTvAGQU69gLOx1kh0
3wuUrZfCR0cmXHmGOs985Gl+dU1cyA/b4KxybZFQOSgxUuDvi9gwmfeS132DgcrU
93CeCpSwAQA45T4/5xuXnYwR0nF1O8qJhVU9PI1etMx4XFe1J2QdZ3LtPQKBgDWq
fAPhS3AKpS7M+ygVsPRM4DY+9IuwGUdKevxBdxUavRpt7mo7I8/zeO4b+QR85q7/
/1gsXkHYSHxIGZD0lEQfgkhGku49MH8DNgQaX38vdxEQYSdIpNk9hxPtwyEJrPs4
CUiEZv0GKIp68Zh+jsFdKo2ovuCp9JKX0JEdBOqZAoGBAL2OdlSO1gpzXXbXe985
p2bV4UR/xR6MMgjUl25jj3Ncn8xUfsOi0IzYzXa0VYXRwhTjlUR/9IGa6qb9ylzl
6h1B/xiJlSvz28AQvcN6LYyxk4xqKzZMyXk9GZk1lObgiAlkLNSGaxSzBwSG/TZl
0DXfpedJbo8yAOwUm3HwYSOU
-----END PRIVATE KEY-----"""

_TEST_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzhHTpU2hCnQhKSChh9kF
+Fx9G8I3JJQWG4i0Rszj0i1O38eR1lN6Cnbp3XK1K9uQKvvTOBAqtCD0JskqXEji
aIuJeIGE5alBRqAFAPQrsdPMZcmsL0gft3IPoMG8VGVijFCJInq35lNV/sSFtGIq
3b+cBqscQbu0+5mYUFO5eD8ZxL9UvXxCqEe+3Ds+pP7TrK10bob49DECCv1rj6SE
8o5AAQ3jwIO5NpaAgMSQNQEQHK78f/tcbG8kSJ8i5lYZIRXH1MHK7PKGI96melve
GuJWOWkmah5hgh0W5Asm7d8zjURW+MWfREh6S9nb49ijSbe8vwBghIS3Q2HaaaY3
3wIDAQAB
-----END PUBLIC KEY-----"""


def _make_provider() -> JwtTokenProvider:
    """Crea una instancia del proveedor de tokens con claves de test.

    Returns:
        Instancia configurada de JwtTokenProvider.
    """
    return JwtTokenProvider(private_key=_TEST_PRIVATE_KEY, public_key=_TEST_PUBLIC_KEY)


def test_create_access_token_when_valid_input_then_returns_jwt() -> None:
    """Caso positivo: genera access token con claims correctos."""
    # Arrange
    provider = _make_provider()

    # Act
    token = provider.create_access_token("user123", "+573001234567")

    # Assert
    claims = jwt.decode(token, _TEST_PUBLIC_KEY, algorithms=["RS256"])
    assert claims["sub"] == "user123"
    assert claims["phone"] == "+573001234567"
    assert claims["type"] == "access"
    assert "exp" in claims
    assert "iat" in claims


def test_create_refresh_token_when_valid_input_then_returns_jwt() -> None:
    """Caso positivo: genera refresh token con claims correctos."""
    # Arrange
    provider = _make_provider()

    # Act
    token = provider.create_refresh_token("user123")

    # Assert
    claims = jwt.decode(token, _TEST_PUBLIC_KEY, algorithms=["RS256"])
    assert claims["sub"] == "user123"
    assert claims["type"] == "refresh"
    assert "phone" not in claims


def test_create_temp_token_when_valid_input_then_returns_jwt_with_mfa_pending() -> None:
    """Caso positivo: genera temp token con claim mfa_pending."""
    # Arrange
    provider = _make_provider()

    # Act
    token = provider.create_temp_token("user123")

    # Assert
    claims = jwt.decode(token, _TEST_PUBLIC_KEY, algorithms=["RS256"])
    assert claims["sub"] == "user123"
    assert claims["type"] == "temp"
    assert claims["mfa_pending"] is True


def test_decode_token_when_valid_access_token_then_returns_claims() -> None:
    """Caso positivo: decodifica token valido correctamente."""
    # Arrange
    provider = _make_provider()
    token = provider.create_access_token("user123", "+573001234567")

    # Act
    claims = provider.decode_token(token)

    # Assert
    assert claims["sub"] == "user123"
    assert claims["phone"] == "+573001234567"
    assert claims["type"] == "access"


def test_decode_token_when_expired_then_raises_value_error() -> None:
    """Caso negativo: token expirado lanza TokenExpiredException."""
    # Arrange
    provider = _make_provider()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user123",
        "type": "access",
        "exp": now - timedelta(seconds=10),
        "iat": now - timedelta(seconds=100),
    }
    token = jwt.encode(payload, _TEST_PRIVATE_KEY, algorithm="RS256")

    # Act & Assert
    with pytest.raises(TokenExpiredException, match="Token has expired"):
        provider.decode_token(token)


def test_decode_token_when_invalid_signature_then_raises_value_error() -> None:
    """Caso negativo: token con firma invalida."""
    # Arrange
    provider = _make_provider()

    # Act & Assert
    with pytest.raises(TokenInvalidException, match="Invalid token"):
        provider.decode_token("invalid.token.signature")


def test_decode_token_when_tampered_then_raises_value_error() -> None:
    """Caso negativo: token manipulado."""
    # Arrange
    provider = _make_provider()
    token = provider.create_access_token("user123", "+573001234567")
    tampered = token[:-5] + "XXXXX"

    # Act & Assert
    with pytest.raises(TokenInvalidException, match="Invalid token"):
        provider.decode_token(tampered)


def test_access_token_when_created_then_expires_in_30_minutes() -> None:
    """Edge case: verifica tiempo de expiracion del access token."""
    # Arrange
    provider = _make_provider()

    # Act
    token = provider.create_access_token("user123", "+573001234567")
    claims = jwt.decode(token, _TEST_PUBLIC_KEY, algorithms=["RS256"])

    # Assert
    exp = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
    iat = datetime.fromtimestamp(claims["iat"], tz=timezone.utc)
    diff = (exp - iat).total_seconds()
    assert 1799 <= diff <= 1801


def test_refresh_token_when_created_then_expires_in_7_days() -> None:
    """Edge case: verifica tiempo de expiracion del refresh token."""
    # Arrange
    provider = _make_provider()

    # Act
    token = provider.create_refresh_token("user123")
    claims = jwt.decode(token, _TEST_PUBLIC_KEY, algorithms=["RS256"])

    # Assert
    exp = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
    iat = datetime.fromtimestamp(claims["iat"], tz=timezone.utc)
    diff = (exp - iat).total_seconds()
    assert 604799 <= diff <= 604801


def test_temp_token_when_created_then_expires_in_5_minutes() -> None:
    """Edge case: verifica tiempo de expiracion del temp token."""
    # Arrange
    provider = _make_provider()

    # Act
    token = provider.create_temp_token("user123")
    claims = jwt.decode(token, _TEST_PUBLIC_KEY, algorithms=["RS256"])

    # Assert
    exp = datetime.fromtimestamp(claims["exp"], tz=timezone.utc)
    iat = datetime.fromtimestamp(claims["iat"], tz=timezone.utc)
    diff = (exp - iat).total_seconds()
    assert 299 <= diff <= 301


def test_decode_token_when_empty_string_then_raises_value_error() -> None:
    """Edge case: token vacio."""
    # Arrange
    provider = _make_provider()

    # Act & Assert
    with pytest.raises(TokenInvalidException, match="Invalid token"):
        provider.decode_token("")
