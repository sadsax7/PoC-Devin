"""
Adaptador de seguridad: TokenProviderImpl (RS256 JWT).

Genera y verifica tokens JWT usando claves asimétricas RS256
con PyJWT. Implementa el contrato ``TokenProviderPort``.

Referencia: HU-BE-02 AC#3, BACKEND-GUIDELINES.md §5.1.6.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt

from app.domain.ports.token_provider_port import TokenProviderPort

# Expiración por defecto según HU-BE-02 AC#3
_ACCESS_EXPIRE_SECONDS = 1800  # 30 minutos
_REFRESH_EXPIRE_SECONDS = 604800  # 7 días
_TEMP_EXPIRE_SECONDS = 300  # 5 minutos
_ALGORITHM = "RS256"


class TokenProviderImpl(TokenProviderPort):
    """Implementación de TokenProviderPort con RS256 y PyJWT.

    Carga claves PEM al instanciarse y las reutiliza para
    firmado y verificación.

    Attributes:
        _private_key: Clave privada RSA en formato PEM.
        _public_key: Clave pública RSA en formato PEM.
        _access_expire: Segundos de vida del access token.
        _refresh_expire: Segundos de vida del refresh token.
        _temp_expire: Segundos de vida del temp token (MFA).
    """

    def __init__(
        self,
        private_key_path: str,
        public_key_path: str,
        access_expire: int = _ACCESS_EXPIRE_SECONDS,
        refresh_expire: int = _REFRESH_EXPIRE_SECONDS,
        temp_expire: int = _TEMP_EXPIRE_SECONDS,
    ) -> None:
        """Inicializa cargando claves PEM desde disco.

        Args:
            private_key_path: Ruta a la clave privada PEM.
            public_key_path: Ruta a la clave pública PEM.
            access_expire: Segundos de expiración para access tokens.
            refresh_expire: Segundos de expiración para refresh tokens.
            temp_expire: Segundos de expiración para temp tokens.
        """
        self._private_key = Path(private_key_path).read_text()
        self._public_key = Path(public_key_path).read_text()
        self._access_expire = access_expire
        self._refresh_expire = refresh_expire
        self._temp_expire = temp_expire

    def generate_access_token(self, user_id: str, phone: str) -> str:
        """Genera un access token JWT RS256.

        Args:
            user_id: ObjectId del usuario como string.
            phone: Teléfono del usuario.

        Returns:
            Token JWT firmado.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "phone": phone,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(seconds=self._access_expire),
        }
        return jwt.encode(payload, self._private_key, algorithm=_ALGORITHM)

    def generate_refresh_token(self, user_id: str) -> str:
        """Genera un refresh token JWT RS256.

        Args:
            user_id: ObjectId del usuario como string.

        Returns:
            Token JWT firmado.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(seconds=self._refresh_expire),
        }
        return jwt.encode(payload, self._private_key, algorithm=_ALGORITHM)

    def generate_temp_token(self, user_id: str) -> str:
        """Genera un temp token JWT RS256 para flujo MFA.

        Args:
            user_id: ObjectId del usuario como string.

        Returns:
            Token JWT firmado con claim mfa_pending=true.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "type": "temp",
            "mfa_pending": True,
            "iat": now,
            "exp": now + timedelta(seconds=self._temp_expire),
        }
        return jwt.encode(payload, self._private_key, algorithm=_ALGORITHM)

    def verify_token(self, token: str) -> dict[str, object]:
        """Verifica y decodifica un token JWT RS256.

        Args:
            token: Token JWT a verificar.

        Returns:
            Claims decodificados del token.

        Raises:
            ValueError: Si el token es inválido o expirado.
        """
        try:
            claims: dict[str, object] = jwt.decode(
                token,
                self._public_key,
                algorithms=[_ALGORITHM],
            )
            return claims
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired") from None
        except jwt.InvalidTokenError as exc:
            raise ValueError(f"Invalid token: {exc}") from None
