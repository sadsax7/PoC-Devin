"""
Puerto: KycVerificationPort.

Abstracción para verificación de identidad (KYC).
Implementado por adapters/outbound/kyc/kyc_client_impl.py.

Referencia: BACKEND-GUIDELINES.md §2.1, §3.4, HU-BE-01 AC#4
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.user import KycStatus


class KycVerificationPort(ABC):
    """Contrato para servicio de verificación KYC."""

    @abstractmethod
    async def verify(self, phone: str) -> KycStatus:
        """Verifica el estado KYC de un número de teléfono.

        Args:
            phone: Número E.164 a verificar.

        Returns:
            KycStatus resultante de la verificación.
        """
        ...
