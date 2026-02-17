"""Puerto del proveedor de tokens JWT del dominio.

Define el contrato para servicios de generacion y validacion
de tokens de autenticacion.
"""

from abc import ABC, abstractmethod
from typing import Dict


class TokenExpiredException(Exception):
    """Excepcion lanzada cuando un token JWT ha expirado."""


class TokenInvalidException(Exception):
    """Excepcion lanzada cuando un token JWT es invalido o tiene firma incorrecta."""


class TokenProviderPort(ABC):
    """Puerto para generacion y validacion de tokens JWT.

    Define la interfaz para emitir access tokens, refresh tokens
    y tokens temporales de MFA, asi como validar tokens existentes.
    """

    @abstractmethod
    def create_access_token(self, user_id: str, phone: str) -> str:
        """Genera un access token JWT.

        Args:
            user_id: Identificador unico del usuario.
            phone: Numero de telefono del usuario.

        Returns:
            Token JWT firmado con claims de acceso.
        """

    @abstractmethod
    def create_refresh_token(self, user_id: str) -> str:
        """Genera un refresh token JWT.

        Args:
            user_id: Identificador unico del usuario.

        Returns:
            Token JWT firmado con claims de renovacion.
        """

    @abstractmethod
    def create_temp_token(self, user_id: str) -> str:
        """Genera un token temporal para flujo MFA.

        Args:
            user_id: Identificador unico del usuario.

        Returns:
            Token JWT firmado con claim mfa_pending.
        """

    @abstractmethod
    def decode_token(self, token: str) -> Dict[str, object]:
        """Decodifica y valida un token JWT.

        Args:
            token: Token JWT a decodificar.

        Returns:
            Diccionario con los claims del token.

        Raises:
            TokenExpiredException: Si el token ha expirado.
            TokenInvalidException: Si el token es invalido o tiene firma incorrecta.
        """
