"""Puerto: MfaVerifierPort.

Define el contrato para verificación de códigos MFA.
Permite al dominio permanecer agnóstico del mecanismo concreto
(TOTP, mock, SMS, etc.).

Referencia: BACKEND-GUIDELINES.md §5.1.1, HU-BE-02 AC#2.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class MfaVerifierPort(ABC):
    """Contrato para verificadores de código MFA."""

    @abstractmethod
    def verify_code(self, code: str) -> bool:
        """Verifica si un código MFA es válido.

        Args:
            code: Código de 6 dígitos proporcionado por el usuario.

        Returns:
            True si el código es correcto, False en caso contrario.
        """
        ...
