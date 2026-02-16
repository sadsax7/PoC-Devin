"""Implementacion mock del servicio de verificacion KYC.

Adaptador de salida que simula un servicio KYC externo
basado en el sufijo del numero de telefono.
"""

from app.domain.ports.kyc_verification_port import KycVerificationPort


class MockKycClient(KycVerificationPort):
    """Cliente mock de verificacion KYC.

    Simula un servicio KYC externo con las siguientes reglas:
        - Telefono termina en '00': rejected
        - Telefono termina en '99': approved
        - Cualquier otro: pending
    """

    async def verify(self, phone: str) -> str:
        """Verifica el estado KYC basado en el sufijo del telefono.

        Args:
            phone: Numero de telefono en formato E.164.

        Returns:
            Estado KYC: 'rejected', 'approved' o 'pending'.
        """
        if phone.endswith("00"):
            return "rejected"
        if phone.endswith("99"):
            return "approved"
        return "pending"
