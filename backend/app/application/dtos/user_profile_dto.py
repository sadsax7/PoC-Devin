"""
DTOs para el caso de uso GetUserProfile.

Define el contrato de salida sanitizado para el perfil del usuario,
alineado con HU-BE-03 AC#3.

Referencia: BACKEND-GUIDELINES.md §5.1.2, HU-BE-03 AC#3.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UserProfileOutputDTO:
    """Salida sanitizada del caso de uso GetUserProfile.

    Excluye password_hash y cualquier campo sensible.
    Cumple HU-BE-03 AC#3 (sanitización de respuesta).

    Attributes:
        user_id: Identificador único del usuario (ObjectId como string).
        phone: Teléfono en formato E.164.
        email: Correo electrónico o None.
        name: Nombre completo o None.
        kyc_status: Estado KYC: "pending" | "approved" | "rejected".
        mfa_enabled: Indica si MFA está habilitado.
        created_at: Timestamp de creación en formato ISO 8601 (UTC, Z-suffix).
    """

    user_id: str
    phone: str
    email: str | None
    name: str | None
    kyc_status: str
    mfa_enabled: bool
    created_at: str
