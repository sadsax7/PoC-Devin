"""Router de autenticacion para la API.

Provee endpoints de registro, login y verificacion MFA
para el sistema de autenticacion.
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.adapters.inbound.http.dependencies.container import (
    get_login_user_use_case,
    get_register_user_use_case,
    get_verify_mfa_use_case,
)
from app.application.dtos.login_user_dto import LoginUserInputDTO
from app.application.dtos.register_user_dto import RegisterUserInputDTO
from app.application.dtos.verify_mfa_dto import VerifyMfaInputDTO
from app.application.use_cases.login_user_use_case import (
    AccountLockedError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.application.use_cases.register_user_use_case import (
    DuplicatePhoneError,
    KycRejectedError,
    ValidationError,
)
from app.application.use_cases.verify_mfa_use_case import (
    InvalidMfaCodeError,
    TempTokenExpiredError,
    TooManyMfaAttemptsError,
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


class LoginRequest(BaseModel):
    """Modelo de solicitud para login de usuario.

    Attributes:
        phone: Numero de telefono en formato E.164.
        password: Contrasena del usuario (8-128 caracteres).
    """

    phone: str
    password: str = Field(min_length=8, max_length=128)


class LoginSuccessResponse(BaseModel):
    """Modelo de respuesta exitosa del login sin MFA.

    Attributes:
        access_token: Token JWT de acceso.
        refresh_token: Token JWT de renovacion.
        token_type: Tipo de token (Bearer).
        expires_in: Tiempo de expiracion en segundos.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 1800


class LoginMfaResponse(BaseModel):
    """Modelo de respuesta del login con MFA requerido.

    Attributes:
        temp_token: Token temporal para verificacion MFA.
        mfa_required: Indica que MFA es requerido.
        message: Mensaje informativo.
    """

    temp_token: str
    mfa_required: bool = True
    message: str = "MFA verification required"


class MfaVerifyRequest(BaseModel):
    """Modelo de solicitud para verificacion MFA.

    Attributes:
        temp_token: Token temporal JWT del login.
        code: Codigo de verificacion de 6 digitos.
    """

    temp_token: str
    code: str = Field(min_length=6, max_length=6)


class MfaVerifyResponse(BaseModel):
    """Modelo de respuesta exitosa de verificacion MFA.

    Attributes:
        access_token: Token JWT de acceso.
        refresh_token: Token JWT de renovacion.
        token_type: Tipo de token (Bearer).
        expires_in: Tiempo de expiracion en segundos.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 1800


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


@router.post(
    "/login",
    summary="Iniciar sesion con telefono y contrasena",
    responses={
        200: {"description": "Login exitoso o MFA requerido"},
        401: {"description": "Credenciales invalidas"},
        404: {"description": "Telefono no registrado"},
        423: {"description": "Cuenta bloqueada por rechazo KYC"},
    },
)
async def login_user(request: LoginRequest) -> Any:
    """Autentica un usuario con telefono y contrasena.

    Args:
        request: Datos de login del usuario.

    Returns:
        LoginSuccessResponse o LoginMfaResponse segun flujo MFA.

    Raises:
        HTTPException: Si hay errores de autenticacion.
    """
    use_case = get_login_user_use_case()

    input_dto = LoginUserInputDTO(
        phone=request.phone,
        password=request.password,
    )

    try:
        result = await use_case.execute(input_dto)
    except UserNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Phone number not registered",
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )
    except AccountLockedError:
        raise HTTPException(
            status_code=423,
            detail="Account locked due to KYC rejection",
        )

    if result.mfa_required:
        return LoginMfaResponse(
            temp_token=result.temp_token or "",
            mfa_required=True,
            message=result.message or "MFA verification required",
        )

    return LoginSuccessResponse(
        access_token=result.access_token or "",
        refresh_token=result.refresh_token or "",
        token_type=result.token_type,
        expires_in=result.expires_in,
    )


@router.post(
    "/mfa/verify",
    response_model=MfaVerifyResponse,
    summary="Verificar codigo MFA y obtener tokens finales",
    responses={
        200: {"description": "MFA verificado exitosamente"},
        401: {"description": "Codigo MFA invalido o token expirado"},
        429: {"description": "Demasiados intentos fallidos"},
    },
)
async def verify_mfa(request: MfaVerifyRequest) -> Any:
    """Verifica codigo MFA y emite tokens de acceso finales.

    Args:
        request: Datos de verificacion MFA.

    Returns:
        MfaVerifyResponse con access y refresh tokens.

    Raises:
        HTTPException: Si hay errores de verificacion MFA.
    """
    use_case = get_verify_mfa_use_case()

    input_dto = VerifyMfaInputDTO(
        temp_token=request.temp_token,
        code=request.code,
    )

    try:
        result = await use_case.execute(input_dto)
    except TempTokenExpiredError:
        raise HTTPException(
            status_code=401,
            detail="Temporary token expired, please login again",
        )
    except TooManyMfaAttemptsError:
        raise HTTPException(
            status_code=429,
            detail="Too many failed MFA attempts, please login again",
        )
    except InvalidMfaCodeError as exc:
        return JSONResponse(
            status_code=401,
            content={
                "detail": "Invalid MFA code",
                "attempts_remaining": exc.attempts_remaining,
            },
        )

    return MfaVerifyResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
        expires_in=result.expires_in,
    )
