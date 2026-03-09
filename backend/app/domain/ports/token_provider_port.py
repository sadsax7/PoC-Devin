"""Puerto: TokenProviderPort.

Define el contrato para generación y verificación de tokens JWT.
El dominio depende solo de esta interfaz, no de PyJWT ni detalles
criptográficos.

Referencia: BACKEND-GUIDELINES.md §5.1.1, HU-BE-02 AC#3.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class TokenProviderPort(ABC):
    """Contrato para proveedores de tokens de autenticación.

    Genera access, refresh y temp (MFA) tokens con claims
    especificados en HU-BE-02 AC#3.
    """

    @abstractmethod
    def generate_access_token(self, user_id: str, phone: str) -> str:
        """Genera un access token JWT.

        Args:
            user_id: Identificador del usuario (sub claim).
            phone: Teléfono del usuario.

        Returns:
            Token JWT firmado.
        """
        ...

    @abstractmethod
    def generate_refresh_token(self, user_id: str) -> str:
        """Genera un refresh token JWT.

        Args:
            user_id: Identificador del usuario (sub claim).

        Returns:
            Token JWT firmado.
        """
        ...

    @abstractmethod
    def generate_temp_token(self, user_id: str) -> str:
        """Genera un temp token JWT para flujo MFA.

        Args:
            user_id: Identificador del usuario (sub claim).

        Returns:
            Token JWT firmado con claim mfa_pending=true.
        """
        ...

    @abstractmethod
    def verify_token(self, token: str) -> dict[str, object]:
        """Verifica y decodifica un token JWT.

        Args:
            token: Token JWT a verificar.

        Returns:
            Claims decodificados del token.

        Raises:
            ValueError: Si el token es inválido, expirado o corrupto.
        """
        ...
