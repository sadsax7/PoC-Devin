"""Caso de uso para registro de usuarios.

Orquesta el flujo de registro: validacion, verificacion KYC,
hashing de contrasena y persistencia del usuario.
"""

from app.application.dtos.register_user_dto import (RegisterUserInputDTO,
                                                    RegisterUserOutputDTO)
from app.domain.entities.user import User
from app.domain.ports.kyc_verification_port import KycVerificationPort
from app.domain.ports.password_hasher_port import PasswordHasherPort
from app.domain.ports.user_repository import UserRepositoryPort
from app.domain.services.registration_service import (validate_email,
                                                      validate_name,
                                                      validate_password)
from app.domain.value_objects.phone_number import PhoneNumber


class DuplicatePhoneError(Exception):
    """Error cuando el telefono ya esta registrado."""


class KycRejectedError(Exception):
    """Error cuando la verificacion KYC es rechazada."""


class ValidationError(Exception):
    """Error de validacion de campos.

    Attributes:
        field: Campo que fallo la validacion.
        message: Mensaje descriptivo del error.
    """

    def __init__(self, field: str, message: str) -> None:
        """Inicializa el error de validacion.

        Args:
            field: Campo que fallo.
            message: Descripcion del error.
        """
        self.field = field
        self.message = message
        super().__init__(message)


class RegisterUserUseCase:
    """Caso de uso para registrar un nuevo usuario.

    Coordina la validacion de datos, verificacion KYC,
    hashing de contrasena y persistencia en el repositorio.
    """

    def __init__(
        self,
        user_repository: UserRepositoryPort,
        kyc_verification: KycVerificationPort,
        password_hasher: PasswordHasherPort,
    ) -> None:
        """Inicializa el caso de uso con sus dependencias.

        Args:
            user_repository: Puerto del repositorio de usuarios.
            kyc_verification: Puerto de verificacion KYC.
            password_hasher: Puerto del hasher de contrasenas.
        """
        self._user_repository = user_repository
        self._kyc_verification = kyc_verification
        self._password_hasher = password_hasher

    async def execute(self, input_dto: RegisterUserInputDTO) -> RegisterUserOutputDTO:
        """Ejecuta el flujo de registro de usuario.

        Args:
            input_dto: Datos de entrada del registro.

        Returns:
            DTO con el user_id del usuario creado.

        Raises:
            ValidationError: Si los datos de entrada no son validos.
            DuplicatePhoneError: Si el telefono ya esta registrado.
            KycRejectedError: Si la verificacion KYC es rechazada.
        """
        self._validate_input(input_dto)

        phone_vo = PhoneNumber(input_dto.phone)

        existing_user = await self._user_repository.find_by_phone(phone_vo.value)
        if existing_user is not None:
            raise DuplicatePhoneError("Phone number already registered")

        kyc_status = await self._kyc_verification.verify(phone_vo.value)
        if kyc_status == "rejected":
            raise KycRejectedError("KYC verification rejected for this phone number")

        password_hash = self._password_hasher.hash_password(input_dto.password)

        user = User(
            phone=phone_vo.value,
            password_hash=password_hash,
            email=input_dto.email,
            name=input_dto.name,
            kyc_status=kyc_status,
            mfa_enabled=False,
        )

        created_user = await self._user_repository.create(user)

        if created_user.id is None:
            raise RuntimeError("User ID was not assigned after creation")

        return RegisterUserOutputDTO(user_id=created_user.id)

    def _validate_input(self, input_dto: RegisterUserInputDTO) -> None:
        """Valida los campos de entrada del registro.

        Args:
            input_dto: Datos de entrada a validar.

        Raises:
            ValidationError: Si algun campo no cumple las reglas.
        """
        password_error = validate_password(input_dto.password)
        if password_error is not None:
            raise ValidationError(field="password", message=password_error)

        if input_dto.email is not None:
            email_error = validate_email(input_dto.email)
            if email_error is not None:
                raise ValidationError(field="email", message=email_error)

        if input_dto.name is not None:
            name_error = validate_name(input_dto.name)
            if name_error is not None:
                raise ValidationError(field="name", message=name_error)
