"""Servicio de dominio para autenticacion de usuarios.

Contiene la logica de negocio pura para validar credenciales
y determinar el flujo de autenticacion (con o sin MFA).
"""

_PASSWORD_MIN_LENGTH = 8
_PASSWORD_MAX_LENGTH = 128


def validate_login_password(password: str) -> bool:
    """Valida que la contrasena cumpla con longitud requerida para login.

    Args:
        password: Contrasena a validar.

    Returns:
        True si la longitud es valida.
    """
    return _PASSWORD_MIN_LENGTH <= len(password) <= _PASSWORD_MAX_LENGTH


def is_account_locked(kyc_status: str) -> bool:
    """Determina si una cuenta esta bloqueada por rechazo KYC.

    Args:
        kyc_status: Estado de verificacion KYC del usuario.

    Returns:
        True si el estado es 'rejected'.
    """
    return kyc_status == "rejected"


def requires_mfa(mfa_enabled: bool) -> bool:
    """Determina si el usuario requiere verificacion MFA.

    Args:
        mfa_enabled: Indica si MFA esta habilitado para el usuario.

    Returns:
        True si MFA esta habilitado.
    """
    return mfa_enabled
