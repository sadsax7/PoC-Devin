"""Servicio de dominio para verificacion MFA.

Contiene la logica de negocio para validar codigos de
autenticacion de dos factores. En esta fase PoC usa
un codigo fijo como simulacion de TOTP real.
"""

_MOCK_MFA_CODE = "123456"


def verify_mfa_code(code: str) -> bool:
    """Verifica un codigo MFA contra el valor esperado.

    En esta fase PoC, el codigo fijo '123456' aprueba la verificacion.
    Preparado para futura integracion con TOTP real.

    Args:
        code: Codigo de 6 digitos proporcionado por el usuario.

    Returns:
        True si el codigo es valido.
    """
    return code == _MOCK_MFA_CODE
