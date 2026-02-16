"""Puerto de verificacion KYC del dominio.

Define el contrato para servicios de verificacion
Know Your Customer (KYC).
"""

from abc import ABC, abstractmethod


class KycVerificationPort(ABC):
    """Puerto para verificacion KYC.

    Define la interfaz para verificar el estado KYC
    de un usuario basado en su numero de telefono.
    """

    @abstractmethod
    async def verify(self, phone: str) -> str:
        """Verifica el estado KYC de un numero de telefono.

        Args:
            phone: Numero de telefono en formato E.164.

        Returns:
            Estado KYC: 'pending', 'approved' o 'rejected'.
        """
