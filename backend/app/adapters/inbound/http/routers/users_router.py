"""Router de usuarios para la API.

Provee endpoints protegidos para consulta de datos
del usuario autenticado.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.adapters.inbound.http.dependencies.auth import get_current_user
from app.adapters.inbound.http.dependencies.container import get_user_profile_use_case
from app.application.dtos.user_profile_dto import UserProfileInputDTO
from app.application.use_cases.get_user_profile_use_case import UserNotFoundError

router = APIRouter(prefix="/users", tags=["users"])


class UserProfileResponse(BaseModel):
    """Modelo de respuesta del perfil de usuario.

    Attributes:
        user_id: Identificador unico del usuario.
        phone: Numero de telefono en formato E.164.
        email: Correo electronico del usuario (opcional).
        name: Nombre del usuario (opcional).
        kyc_status: Estado de verificacion KYC.
        mfa_enabled: Indica si MFA esta habilitado.
        created_at: Fecha y hora de creacion en formato ISO 8601.
    """

    user_id: str
    phone: str
    email: Optional[str] = None
    name: Optional[str] = None
    kyc_status: str
    mfa_enabled: bool
    created_at: str


@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Obtener perfil del usuario autenticado",
    responses={
        401: {"description": "Token invalido, expirado o ausente"},
        404: {"description": "Usuario no encontrado"},
    },
)
async def get_user_profile(
    user_id: str = Depends(get_current_user),
) -> UserProfileResponse:
    """Retorna los datos del perfil del usuario autenticado.

    Args:
        user_id: ID del usuario extraido del token JWT.

    Returns:
        UserProfileResponse con los datos sanitizados del perfil.

    Raises:
        HTTPException: 404 si el usuario no existe.
    """
    use_case = get_user_profile_use_case()
    input_dto = UserProfileInputDTO(user_id=user_id)

    try:
        result = await use_case.execute(input_dto)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfileResponse(
        user_id=result.user_id,
        phone=result.phone,
        email=result.email,
        name=result.name,
        kyc_status=result.kyc_status,
        mfa_enabled=result.mfa_enabled,
        created_at=result.created_at,
    )
