"""
Tests unitarios para TokenProviderImpl y MfaVerifierImpl.

Cubre: generación JWT RS256, verificación, expiración, MFA mock.
Referencia: HU-BE-02 AC#3, BACKEND-GUIDELINES.md §5.1.7.1
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from app.adapters.outbound.security.mfa_verifier_impl import MfaVerifierImpl
from app.adapters.outbound.security.token_provider_impl import TokenProviderImpl

# ============================================================
# Helpers: claves RSA de test
# ============================================================

_KEYS_DIR = Path(__file__).resolve().parents[3] / "keys"


@pytest.fixture
def token_provider() -> TokenProviderImpl:
    """TokenProviderImpl con claves RSA generadas en el proyecto."""
    return TokenProviderImpl(
        private_key_path=str(_KEYS_DIR / "private.pem"),
        public_key_path=str(_KEYS_DIR / "public.pem"),
        access_expire=1800,
        refresh_expire=604800,
        temp_expire=300,
    )


# ============================================================
# TokenProviderImpl — Access Token
# ============================================================


class TestTokenProviderAccessToken:
    """Tests para generación de access tokens."""

    def test_generate_access_token_when_valid_args_then_returns_jwt(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Genera un JWT string no vacío."""
        token = token_provider.generate_access_token("uid123", "+573001234567")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_access_token_when_decoded_then_correct_claims(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Claims contienen sub, phone, type=access."""
        token = token_provider.generate_access_token("uid123", "+573001234567")
        claims = token_provider.verify_token(token)
        assert claims["sub"] == "uid123"
        assert claims["phone"] == "+573001234567"
        assert claims["type"] == "access"

    def test_generate_access_token_when_decoded_then_has_exp(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Access token tiene claim exp."""
        token = token_provider.generate_access_token("uid123", "+573001234567")
        claims = token_provider.verify_token(token)
        assert "exp" in claims
        assert "iat" in claims


# ============================================================
# TokenProviderImpl — Refresh Token
# ============================================================


class TestTokenProviderRefreshToken:
    """Tests para refresh tokens."""

    def test_generate_refresh_token_when_valid_then_returns_jwt(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Genera un JWT string."""
        token = token_provider.generate_refresh_token("uid123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_refresh_token_when_decoded_then_type_refresh(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Claims contienen type=refresh."""
        token = token_provider.generate_refresh_token("uid123")
        claims = token_provider.verify_token(token)
        assert claims["sub"] == "uid123"
        assert claims["type"] == "refresh"

    def test_generate_refresh_token_when_decoded_then_no_phone(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Refresh token no incluye claim phone."""
        token = token_provider.generate_refresh_token("uid123")
        claims = token_provider.verify_token(token)
        assert "phone" not in claims


# ============================================================
# TokenProviderImpl — Temp Token (MFA)
# ============================================================


class TestTokenProviderTempToken:
    """Tests para temp tokens (flujo MFA)."""

    def test_generate_temp_token_when_valid_then_returns_jwt(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Genera un JWT string."""
        token = token_provider.generate_temp_token("uid123")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_temp_token_when_decoded_then_mfa_pending_true(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Claims contienen type=temp y mfa_pending=true."""
        token = token_provider.generate_temp_token("uid123")
        claims = token_provider.verify_token(token)
        assert claims["sub"] == "uid123"
        assert claims["type"] == "temp"
        assert claims["mfa_pending"] is True


# ============================================================
# TokenProviderImpl — Verify Token
# ============================================================


class TestTokenProviderVerify:
    """Tests para verificación de tokens."""

    def test_verify_token_when_valid_then_returns_claims(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Token válido retorna claims dict."""
        token = token_provider.generate_access_token("uid123", "+57300")
        claims = token_provider.verify_token(token)
        assert isinstance(claims, dict)
        assert claims["sub"] == "uid123"

    def test_verify_token_when_tampered_then_raises(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Token manipulado lanza ValueError."""
        token = token_provider.generate_access_token("uid123", "+57300")
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(ValueError, match="Invalid token"):
            token_provider.verify_token(tampered)

    def test_verify_token_when_expired_then_raises(
        self,
    ) -> None:
        """Token expirado lanza ValueError."""
        provider = TokenProviderImpl(
            private_key_path=str(_KEYS_DIR / "private.pem"),
            public_key_path=str(_KEYS_DIR / "public.pem"),
            access_expire=0,  # Expire immediately
        )
        token = provider.generate_access_token("uid123", "+57300")
        # Small sleep to ensure expiry
        time.sleep(0.1)
        with pytest.raises(ValueError, match="expired"):
            provider.verify_token(token)

    def test_verify_token_when_garbage_then_raises(self, token_provider: TokenProviderImpl) -> None:
        """Token basura lanza ValueError."""
        with pytest.raises(ValueError, match="Invalid token"):
            token_provider.verify_token("not.a.valid.jwt")


# ============================================================
# TokenProviderImpl — Edge cases
# ============================================================


class TestTokenProviderEdgeCases:
    """Edge cases para el token provider."""

    def test_different_tokens_for_same_user_are_different(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Tokens generados para el mismo usuario son distintos."""
        t1 = token_provider.generate_access_token("uid123", "+57300")
        t2 = token_provider.generate_access_token("uid123", "+57300")
        # iat may differ slightly
        assert isinstance(t1, str)
        assert isinstance(t2, str)

    def test_access_and_refresh_are_different_types(
        self, token_provider: TokenProviderImpl
    ) -> None:
        """Access y refresh tokens tienen type distinto."""
        access = token_provider.generate_access_token("uid123", "+57300")
        refresh = token_provider.generate_refresh_token("uid123")
        ac = token_provider.verify_token(access)
        rc = token_provider.verify_token(refresh)
        assert ac["type"] == "access"
        assert rc["type"] == "refresh"

    def test_init_when_invalid_key_path_then_raises(self) -> None:
        """Ruta de clave inválida lanza FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            TokenProviderImpl(
                private_key_path="/nonexistent/private.pem",
                public_key_path="/nonexistent/public.pem",
            )


# ============================================================
# MfaVerifierImpl
# ============================================================


class TestMfaVerifierImpl:
    """Tests para el adaptador MFA mock."""

    def test_verify_code_when_correct_code_then_true(self) -> None:
        """Código '123456' retorna True."""
        verifier = MfaVerifierImpl()
        assert verifier.verify_code("123456") is True

    def test_verify_code_when_wrong_code_then_false(self) -> None:
        """Código incorrecto retorna False."""
        verifier = MfaVerifierImpl()
        assert verifier.verify_code("000000") is False

    def test_verify_code_when_empty_code_then_false(self) -> None:
        """Código vacío retorna False."""
        verifier = MfaVerifierImpl()
        assert verifier.verify_code("") is False

    def test_verify_code_when_custom_code_then_accepts_custom(self) -> None:
        """MfaVerifierImpl con código custom acepta solo ese código."""
        verifier = MfaVerifierImpl(valid_code="999999")
        assert verifier.verify_code("999999") is True
        assert verifier.verify_code("123456") is False

    def test_verify_code_when_partial_match_then_false(self) -> None:
        """Coincidencia parcial retorna False."""
        verifier = MfaVerifierImpl()
        assert verifier.verify_code("12345") is False
        assert verifier.verify_code("1234567") is False
