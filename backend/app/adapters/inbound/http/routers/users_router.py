"""
Router de usuarios — GET /users/me.

Expone los datos del perfil del usuario autenticado.
Solo acepta access tokens válidos (RS256, 'type': 'access').

Referencia: HU-BE-03 AC#1-4, BACKEND-GUIDELINES.md §2.3
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.adapters.inbound.http.dependencies.auth_deps import get_current_user
from app.adapters.inbound.http.dependencies.container import (
    get_get_user_profile_use_case,
)
from app.application.use_cases.get_user_profile import (
    GetUserProfileUseCase,
    UserProfileNotFoundError,
)

router = APIRouter(prefix="/users", tags=["Users"])


# ── Pydantic response model ────────────────────────────────────


class UserProfileResponse(BaseModel):
    """Respuesta sanitizada del perfil del usuario autenticado.

    Excluye password_hash y campos sensibles internos.
    Cumple HU-BE-03 AC#3.

    Attributes:
        user_id: Identificador único (ObjectId como string).
        phone: Teléfono en formato E.164.
        email: Correo electrónico o null.
        name: Nombre completo o null.
        kyc_status: Estado KYC: "pending" | "approved" | "rejected".
        mfa_enabled: Si el usuario tiene MFA habilitado.
        created_at: Fecha de creación en ISO 8601 (UTC, Z-suffix).
    """

    user_id: str = Field(..., description="ObjectId del usuario como string")
    phone: str = Field(..., description="Teléfono en formato E.164")
    email: str | None = Field(default=None, description="Correo electrónico")
    name: str | None = Field(default=None, description="Nombre completo")
    kyc_status: str = Field(..., description="Estado KYC: pending | approved | rejected")
    mfa_enabled: bool = Field(..., description="Si MFA está habilitado")
    created_at: str = Field(..., description="Timestamp ISO 8601 UTC")


# ── Endpoints ─────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener perfil del usuario autenticado",
    responses={
        401: {"description": "Token inválido, expirado, ausente o de tipo incorrecto"},
        404: {"description": "Usuario no encontrado"},
    },
)
async def get_my_profile(
    user_id: str = Depends(get_current_user),
    use_case: GetUserProfileUseCase = Depends(get_get_user_profile_use_case),
) -> UserProfileResponse:
    """Retorna los datos del perfil del usuario autenticado.

    Requiere header ``Authorization: Bearer <access_token>``.

    Args:
        user_id: Extraído del JWT por la dependencia get_current_user.
        use_case: Caso de uso GetUserProfile inyectado por el contenedor.

    Returns:
        Perfil sanitizado del usuario.

    Raises:
        HTTPException 401: Token inválido, expirado, ausente o de tipo incorrecto.
        HTTPException 404: Usuario eliminado después de emitir el token.
    """
    try:
        dto = await use_case.execute(user_id)
    except UserProfileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from exc

    return UserProfileResponse(
        user_id=dto.user_id,
        phone=dto.phone,
        email=dto.email,
        name=dto.name,
        kyc_status=dto.kyc_status,
        mfa_enabled=dto.mfa_enabled,
        created_at=dto.created_at,
    )
