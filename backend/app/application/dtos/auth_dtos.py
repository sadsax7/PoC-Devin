"""
DTOs para los casos de uso de autenticación (Login y MFA).

Definen los contratos de entrada y salida para login y
verificación MFA, alineados con HU-BE-02 AC#7.

Referencia: BACKEND-GUIDELINES.md §5.1.2, HU-BE-02 AC#1-#3.
"""

from __future__ import annotations

from dataclasses import dataclass

# ── Login ─────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class LoginInputDTO:
    """Entrada del caso de uso Login.

    Attributes:
        phone: Teléfono en formato E.164.
        password: Contraseña en texto plano.
    """

    phone: str
    password: str


@dataclass(frozen=True, slots=True)
class LoginOutputDTO:
    """Salida del caso de uso Login (sin MFA).

    Attributes:
        access_token: JWT de acceso.
        refresh_token: JWT de refresco.
        token_type: Tipo de token (Bearer).
        expires_in: Segundos hasta expiración del access token.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_in: int = 1800


@dataclass(frozen=True, slots=True)
class LoginMfaRequiredDTO:
    """Salida del caso de uso Login cuando MFA es requerido.

    Attributes:
        temp_token: JWT temporal para flujo MFA.
        mfa_required: Flag indicando que se requiere MFA.
        message: Mensaje informativo.
    """

    temp_token: str
    mfa_required: bool = True
    message: str = "MFA verification required"


# ── MFA Verify ────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class VerifyMfaInputDTO:
    """Entrada del caso de uso VerifyMfa.

    Attributes:
        temp_token: JWT temporal obtenido en login.
        code: Código MFA de 6 dígitos.
    """

    temp_token: str
    code: str


@dataclass(frozen=True, slots=True)
class VerifyMfaOutputDTO:
    """Salida del caso de uso VerifyMfa (éxito).

    Attributes:
        access_token: JWT de acceso final.
        refresh_token: JWT de refresco.
        token_type: Tipo de token (Bearer).
        expires_in: Segundos hasta expiración del access token.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_in: int = 1800
