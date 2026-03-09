"""
Router de autenticación — POST /auth/register.

Adapta peticiones HTTP al caso de uso RegisterUser
y traduce excepciones de dominio a respuestas HTTP.

Referencia: HU-BE-01 AC#7, BACKEND-GUIDELINES.md §2.3
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.adapters.inbound.http.dependencies.container import get_register_user_use_case
from app.application.dtos.register_user_dto import RegisterUserInputDTO
from app.application.use_cases.register_user import (
    DuplicatePhoneError,
    EmailValidationError,
    KycRejectedError,
    NameValidationError,
    PasswordValidationError,
    RegisterUserUseCase,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ── Pydantic request / response models ────────────────────────


class RegisterRequest(BaseModel):
    """Cuerpo de la petición POST /auth/register.

    Attributes:
        phone: Teléfono E.164 (requerido).
        password: Contraseña en texto plano (requerido).
        email: Correo electrónico (opcional, max 255).
        name: Nombre del usuario (opcional, max 100).
    """

    phone: str = Field(..., description="Teléfono en formato E.164, ej: +573001234567")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Contraseña (8-128 chars, mayúsculas, minúsculas, dígitos, especiales)",
    )
    email: str | None = Field(
        default=None,
        max_length=255,
        description="Correo electrónico (opcional)",
    )
    name: str | None = Field(
        default=None,
        max_length=100,
        description="Nombre del usuario (opcional)",
    )


class RegisterResponse(BaseModel):
    """Respuesta exitosa de POST /auth/register.

    Attributes:
        user_id: ID generado del usuario.
    """

    user_id: str


class ErrorDetail(BaseModel):
    """Detalle individual de error de validación.

    Attributes:
        loc: Ubicación del campo con error.
        msg: Mensaje descriptivo del error.
        type: Tipo de error.
    """

    loc: list[str]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Respuesta de error de validación 422.

    Attributes:
        detail: Lista de errores de validación.
    """

    detail: list[ErrorDetail]


# ── Endpoint ──────────────────────────────────────────────────


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
    responses={
        400: {"description": "KYC verification rejected"},
        409: {"description": "Phone number already registered"},
        422: {"description": "Validation error"},
    },
    summary="Registrar un nuevo usuario",
)
async def register_user(
    body: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> RegisterResponse:
    """Registra un nuevo usuario en el sistema.

    Flujo:
    1. Valida contraseña, teléfono, email y nombre.
    2. Verifica unicidad de teléfono.
    3. Hash de contraseña con Argon2.
    4. Verificación KYC (mock).
    5. Persiste el usuario.
    6. Publica evento ``UserRegistered``.

    Args:
        body: Datos de registro del usuario.
        use_case: Caso de uso inyectado vía DI.

    Returns:
        RegisterResponse con el user_id generado.

    Raises:
        HTTPException: Según el tipo de error de dominio.
    """
    input_dto = RegisterUserInputDTO(
        phone=body.phone,
        password=body.password,
        email=body.email,
        name=body.name,
    )

    try:
        output = await use_case.execute(input_dto)
    except DuplicatePhoneError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        ) from None
    except PasswordValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {"loc": ["body", "password"], "msg": msg, "type": "value_error"}
                for msg in exc.errors
            ],
        ) from None
    except KycRejectedError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KYC verification rejected for this phone number",
        ) from None
    except (ValueError, EmailValidationError, NameValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from None

    return RegisterResponse(user_id=output.user_id)
