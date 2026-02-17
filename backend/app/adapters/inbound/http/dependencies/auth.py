"""Dependencia de autenticacion JWT para endpoints protegidos.

Extrae y valida el token Bearer del header Authorization,
verificando firma, expiracion y tipo de token.
"""

from fastapi import HTTPException, Request

from app.adapters.inbound.http.dependencies.container import _get_token_provider
from app.domain.ports.token_provider_port import (
    TokenExpiredException,
    TokenInvalidException,
)


async def get_current_user(request: Request) -> str:
    """Extrae y valida el token JWT del header Authorization.

    Args:
        request: Objeto de solicitud HTTP de FastAPI.

    Returns:
        user_id (sub) extraido del payload JWT.

    Raises:
        HTTPException: 401 si el token es invalido, expirado o de tipo incorrecto.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token = parts[1]
    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    token_provider = _get_token_provider()

    try:
        payload = token_provider.decode_token(token)
    except TokenExpiredException as exc:
        raise HTTPException(status_code=401, detail="Token has expired") from exc
    except TokenInvalidException as exc:
        raise HTTPException(status_code=401, detail="Invalid token signature") from exc

    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(status_code=401, detail="Invalid token type, access token required")

    sub = payload.get("sub")
    if not isinstance(sub, str) or not sub:
        raise HTTPException(status_code=401, detail="Invalid token signature")

    return sub
