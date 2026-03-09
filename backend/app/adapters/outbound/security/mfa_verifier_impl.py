"""
Adaptador de seguridad: MfaVerifierImpl (mock para PoC).

Verificador MFA de demostración que acepta un código fijo.
Cumple el contrato ``MfaVerifierPort`` y será reemplazado
por un adaptador real (TOTP / SMS OTP) en iteraciones futuras.

Referencia: HU-BE-02 AC#3, BACKEND-GUIDELINES.md §5.1.4.
"""

from __future__ import annotations

import logging

from app.domain.ports.mfa_verifier_port import MfaVerifierPort

logger = logging.getLogger(__name__)

_MOCK_VALID_CODE = "123456"


class MfaVerifierImpl(MfaVerifierPort):
    """Implementación mock de MfaVerifierPort para PoC.

    Acepta exclusivamente el código ``123456`` como válido.
    En producción se sustituirá por un adaptador TOTP
    (e.g. pyotp) o integración SMS.

    Attributes:
        _valid_code: Código estático aceptado en modo mock.
    """

    def __init__(self, valid_code: str = _MOCK_VALID_CODE) -> None:
        """Inicializa el verificador MFA mock.

        Args:
            valid_code: Código MFA que se considera válido.
        """
        self._valid_code = valid_code

    def verify_code(self, code: str) -> bool:
        """Verifica si el código MFA proporcionado es válido.

        Args:
            code: Código MFA ingresado por el usuario.

        Returns:
            ``True`` si coincide con el código mock, ``False`` en
            caso contrario.
        """
        is_valid = code == self._valid_code
        logger.info(
            "MFA verification attempt",
            extra={
                "event": "mfa_verification_attempt",
                "is_valid": is_valid,
            },
        )
        return is_valid
