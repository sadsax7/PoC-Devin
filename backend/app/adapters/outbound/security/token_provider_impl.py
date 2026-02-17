"""Implementacion del proveedor de tokens JWT con RS256.

Adaptador de salida que implementa el puerto TokenProviderPort
usando PyJWT con claves asimetricas RSA.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt

from app.domain.ports.token_provider_port import (
    TokenExpiredException,
    TokenInvalidException,
    TokenProviderPort,
)

_ACCESS_TOKEN_EXPIRE_SECONDS = 1800
_REFRESH_TOKEN_EXPIRE_SECONDS = 604800
_TEMP_TOKEN_EXPIRE_SECONDS = 300


class JwtTokenProvider(TokenProviderPort):
    """Implementacion de proveedor de tokens JWT con RS256.

    Utiliza PyJWT con claves RSA asimetricas para firmar
    y verificar tokens de autenticacion.
    """

    def __init__(self, private_key: str, public_key: str) -> None:
        """Inicializa el proveedor con claves RSA.

        Args:
            private_key: Clave privada RSA en formato PEM.
            public_key: Clave publica RSA en formato PEM.
        """
        self._private_key = private_key
        self._public_key = public_key

    def create_access_token(self, user_id: str, phone: str) -> str:
        """Genera un access token JWT con RS256.

        Args:
            user_id: Identificador unico del usuario.
            phone: Numero de telefono del usuario.

        Returns:
            Token JWT firmado con claims de acceso.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "phone": phone,
            "type": "access",
            "exp": now + timedelta(seconds=_ACCESS_TOKEN_EXPIRE_SECONDS),
            "iat": now,
        }
        return jwt.encode(payload, self._private_key, algorithm="RS256")

    def create_refresh_token(self, user_id: str) -> str:
        """Genera un refresh token JWT con RS256.

        Args:
            user_id: Identificador unico del usuario.

        Returns:
            Token JWT firmado con claims de renovacion.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "exp": now + timedelta(seconds=_REFRESH_TOKEN_EXPIRE_SECONDS),
            "iat": now,
        }
        return jwt.encode(payload, self._private_key, algorithm="RS256")

    def create_temp_token(self, user_id: str) -> str:
        """Genera un token temporal para flujo MFA con RS256.

        Args:
            user_id: Identificador unico del usuario.

        Returns:
            Token JWT firmado con claim mfa_pending.
        """
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "mfa_pending": True,
            "type": "temp",
            "exp": now + timedelta(seconds=_TEMP_TOKEN_EXPIRE_SECONDS),
            "iat": now,
        }
        return jwt.encode(payload, self._private_key, algorithm="RS256")

    def decode_token(self, token: str) -> Dict[str, object]:
        """Decodifica y valida un token JWT con RS256.

        Args:
            token: Token JWT a decodificar.

        Returns:
            Diccionario con los claims del token.

        Raises:
            TokenExpiredException: Si el token ha expirado.
            TokenInvalidException: Si el token es invalido o con firma incorrecta.
        """
        try:
            payload: Dict[str, object] = jwt.decode(
                token,
                self._public_key,
                algorithms=["RS256"],
            )
            return payload
        except jwt.ExpiredSignatureError as exc:
            raise TokenExpiredException("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise TokenInvalidException(f"Invalid token: {exc}") from exc
