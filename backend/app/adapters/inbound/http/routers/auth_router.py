"""
Router de autenticación — POST /auth/register, POST /auth/login, POST /auth/mfa/verify.

Adapta peticiones HTTP a casos de uso de autenticación
y traduce excepciones de dominio a respuestas HTTP.

Referencia: HU-BE-01 AC#7, HU-BE-02 AC#1-3, BACKEND-GUIDELINES.md §2.3
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.adapters.inbound.http.dependencies.container import (
    get_login_user_use_case,
    get_register_user_use_case,
    get_verify_mfa_use_case,
)
from app.application.dtos.auth_dtos import LoginInputDTO, VerifyMfaInputDTO
from app.application.dtos.register_user_dto import RegisterUserInputDTO
from app.application.use_cases.login_user import (
    AccountLockedError,
    InvalidCredentialsError,
    LoginUserUseCase,
    UserNotFoundError,
)
from app.application.use_cases.register_user import (
    DuplicatePhoneError,
    EmailValidationError,
    KycRejectedError,
    NameValidationError,
    PasswordValidationError,
    RegisterUserUseCase,
)
from app.application.use_cases.verify_mfa import (
    InvalidMfaCodeError,
    InvalidTempTokenError,
    TooManyMfaAttemptsError,
    VerifyMfaUseCase,
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


# ── Login Pydantic models ────────────────────────────────────


class LoginRequest(BaseModel):
    """Cuerpo de la petición POST /auth/login.

    Attributes:
        phone: Teléfono E.164.
        password: Contraseña en texto plano.
    """

    phone: str = Field(..., description="Teléfono en formato E.164")
    password: str = Field(..., min_length=1, description="Contraseña")


class LoginSuccessResponse(BaseModel):
    """Respuesta exitosa de login sin MFA.

    Attributes:
        access_token: JWT de acceso.
        refresh_token: JWT de refresco.
        token_type: Tipo de token (Bearer).
        expires_in: Segundos de vida del access token.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_in: int = 1800


class LoginMfaResponse(BaseModel):
    """Respuesta cuando se requiere verificación MFA.

    Attributes:
        temp_token: Token temporal para flujo MFA.
        mfa_required: Flag indicando MFA.
        message: Mensaje descriptivo.
    """

    temp_token: str
    mfa_required: bool = True
    message: str = "MFA verification required"


class MfaVerifyRequest(BaseModel):
    """Cuerpo de la petición POST /auth/mfa/verify.

    Attributes:
        temp_token: Token temporal del flujo MFA.
        code: Código MFA de 6 dígitos.
    """

    temp_token: str = Field(..., description="Temp token del login")
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        description="Código MFA de 6 dígitos",
    )


class MfaVerifyResponse(BaseModel):
    """Respuesta exitosa de verificación MFA.

    Attributes:
        access_token: JWT de acceso.
        refresh_token: JWT de refresco.
        token_type: Tipo de token (Bearer).
        expires_in: Segundos de vida del access token.
    """

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"  # noqa: S105
    expires_in: int = 1800


# ── Login Endpoint ────────────────────────────────────────────


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=None,
    responses={
        200: {"description": "Login successful or MFA required"},
        401: {"description": "Invalid credentials"},
        423: {"description": "Account locked"},
    },
    summary="Autenticar un usuario",
)
async def login_user(
    body: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
) -> dict[str, Any]:
    """Autentica un usuario con teléfono y contraseña.

    Flujo:
    1. Busca usuario por teléfono.
    2. Verifica credenciales.
    3. Si MFA habilitado → retorna temp_token.
    4. Si MFA deshabilitado → retorna access + refresh tokens.

    Args:
        body: Datos de login.
        use_case: Caso de uso inyectado vía DI.

    Returns:
        LoginSuccessResponse o LoginMfaResponse.

    Raises:
        HTTPException: Según error de dominio.
    """
    input_dto = LoginInputDTO(phone=body.phone, password=body.password)

    try:
        result = await use_case.execute(input_dto)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from None
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        ) from None
    except AccountLockedError:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account locked due to KYC rejection",
        ) from None

    from app.application.dtos.auth_dtos import LoginMfaRequiredDTO

    if isinstance(result, LoginMfaRequiredDTO):
        return LoginMfaResponse(
            temp_token=result.temp_token,
            mfa_required=True,
            message=result.message,
        ).model_dump()

    return LoginSuccessResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
        token_type=result.token_type,
        expires_in=result.expires_in,
    ).model_dump()


# ── MFA Verify Endpoint ──────────────────────────────────────


@router.post(
    "/mfa/verify",
    status_code=status.HTTP_200_OK,
    response_model=MfaVerifyResponse,
    responses={
        200: {"description": "MFA verification successful"},
        401: {"description": "Invalid MFA code or temp token"},
        429: {"description": "Too many MFA attempts"},
    },
    summary="Verificar código MFA",
)
async def verify_mfa(
    body: MfaVerifyRequest,
    use_case: VerifyMfaUseCase = Depends(get_verify_mfa_use_case),
) -> MfaVerifyResponse:
    """Verifica código MFA y emite tokens finales.

    Flujo:
    1. Valida temp_token JWT.
    2. Verifica código MFA.
    3. Emite access + refresh tokens.

    Args:
        body: Datos de verificación MFA.
        use_case: Caso de uso inyectado vía DI.

    Returns:
        MfaVerifyResponse con tokens finales.

    Raises:
        HTTPException: Según error de dominio.
    """
    input_dto = VerifyMfaInputDTO(
        temp_token=body.temp_token,
        code=body.code,
    )

    try:
        result = await use_case.execute(input_dto)
    except InvalidTempTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Temporary token expired, please login again",
        ) from None
    except TooManyMfaAttemptsError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed MFA attempts, please login again",
        ) from None
    except InvalidMfaCodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid MFA code, {exc.attempts_remaining} attempts remaining",
        ) from None

    return MfaVerifyResponse(
        access_token=result.access_token,
        refresh_token=result.refresh_token,
    )
