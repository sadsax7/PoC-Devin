"""
Dependencia FastAPI para autenticación por JWT.

Extrae y valida el token Bearer del header Authorization,
retornando el user_id (sub) del token.
Reutilizable en cualquier endpoint protegido.

Cumple HU-BE-03 AC#1 y AC#4.

Referencia: BACKEND-GUIDELINES.md §5.1.6, §5.1.1, HU-BE-03.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.adapters.inbound.http.dependencies.container import get_token_provider
from app.domain.ports.token_provider_port import TokenProviderPort

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    token_provider: TokenProviderPort = Depends(get_token_provider),
) -> str:
    """Extrae y valida el JWT Bearer del header Authorization.

    Verifica firma RS256, expiración y que sea un access token.
    Retorna el user_id (claim ``sub``) si es válido.

    Args:
        credentials: Credenciales HTTP Bearer extraídas por FastAPI.
        token_provider: Puerto de verificación de tokens.

    Returns:
        user_id (sub del JWT) como string.

    Raises:
        HTTPException 401: Si falta el token, está expirado,
            tiene firma inválida o es de tipo incorrecto.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raw_token = credentials.credentials

    try:
        claims = token_provider.verify_token(raw_token)
    except ValueError as exc:
        error_message = str(exc).lower()
        if "expired" in error_message:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    token_type = claims.get("type")
    if token_type != "access":  # noqa: S105
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type, access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = claims.get("sub")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id
