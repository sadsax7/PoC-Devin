"""
Adapter: KycClientMock.

Implementación mock del puerto KycVerificationPort.
Simula verificación KYC basada en sufijo del teléfono.

Referencia: BACKEND-GUIDELINES.md §2.4, §3.4, HU-BE-01 AC#4
"""

from __future__ import annotations

from app.domain.entities.user import KycStatus
from app.domain.ports.kyc_verification_port import KycVerificationPort


class KycClientMock(KycVerificationPort):
    """Mock de verificación KYC basado en sufijo telefónico.

    Reglas (HU-BE-01 AC#4):
    - Teléfono termina en "00" → REJECTED
    - Teléfono termina en "99" → APPROVED
    - Cualquier otro → PENDING
    """

    async def verify(self, phone: str) -> KycStatus:
        """Verifica KYC simulado por sufijo de teléfono.

        Args:
            phone: Número E.164.

        Returns:
            KycStatus según regla de sufijo.
        """
        if phone.endswith("00"):
            return KycStatus.REJECTED
        if phone.endswith("99"):
            return KycStatus.APPROVED
        return KycStatus.PENDING
