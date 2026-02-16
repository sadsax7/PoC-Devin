"""Router de autenticacion para la API.

Provee el endpoint POST /auth/register para registrar
nuevos usuarios en el sistema.
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.adapters.inbound.http.dependencies.container import get_register_user_use_case
from app.application.dtos.register_user_dto import RegisterUserInputDTO
from app.application.use_cases.register_user_use_case import (
    DuplicatePhoneError,
    KycRejectedError,
    ValidationError,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    """Modelo de solicitud para registro de usuario.

    Attributes:
        phone: Numero de telefono en formato E.164.
        password: Contrasena del usuario.
        email: Correo electronico (opcional).
        name: Nombre del usuario (opcional).
    """

    phone: str
    password: str
    email: Optional[str] = None
    name: Optional[str] = Field(default=None, max_length=100)


class RegisterResponse(BaseModel):
    """Modelo de respuesta exitosa del registro.

    Attributes:
        user_id: Identificador unico del usuario creado.
    """

    user_id: str


class ErrorDetail(BaseModel):
    """Detalle de error de validacion.

    Attributes:
        loc: Ubicacion del campo con error.
        msg: Mensaje descriptivo del error.
        type: Tipo de error.
    """

    loc: list[str]
    msg: str
    type: str


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=201,
    summary="Registrar un nuevo usuario",
    responses={
        400: {"description": "KYC verification rejected"},
        409: {"description": "Phone number already registered"},
        422: {"description": "Validation error"},
    },
)
async def register_user(request: RegisterRequest) -> Any:
    """Registra un nuevo usuario en el sistema.

    Args:
        request: Datos de registro del usuario.

    Returns:
        RegisterResponse con el user_id generado.

    Raises:
        HTTPException: Si hay errores de validacion, duplicados o KYC.
    """
    use_case = get_register_user_use_case()

    input_dto = RegisterUserInputDTO(
        phone=request.phone,
        password=request.password,
        email=request.email,
        name=request.name,
    )

    try:
        result = await use_case.execute(input_dto)
    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", exc.field],
                    "msg": exc.message,
                    "type": "value_error",
                }
            ],
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["body", "phone"],
                    "msg": str(exc),
                    "type": "value_error",
                }
            ],
        ) from exc
    except DuplicatePhoneError:
        raise HTTPException(
            status_code=409,
            detail="Phone number already registered",
        )
    except KycRejectedError:
        raise HTTPException(
            status_code=400,
            detail="KYC verification rejected for this phone number",
        )

    return RegisterResponse(user_id=result.user_id)
