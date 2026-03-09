"""
Caso de uso: Registrar Usuario.

Orquesta la validación, hashing, verificación KYC y persistencia
de un nuevo usuario en el sistema.

Referencia: BACKEND-GUIDELINES.md §2.2, §3.2, HU-BE-01
"""

from __future__ import annotations

from app.application.dtos.register_user_dto import RegisterUserInputDTO, RegisterUserOutputDTO
from app.domain.entities.user import KycStatus, User
from app.domain.ports.event_publisher_port import EventPublisherPort
from app.domain.ports.kyc_verification_port import KycVerificationPort
from app.domain.ports.password_hasher_port import PasswordHasherPort
from app.domain.ports.user_repository import UserRepository
from app.domain.value_objects.hashed_password import HashedPassword
from app.domain.value_objects.phone_number import PhoneNumber


class DuplicatePhoneError(Exception):
    """El teléfono ya está registrado (409 Conflict)."""


class PasswordValidationError(Exception):
    """La contraseña no cumple las reglas de validación (422).

    Attributes:
        errors: Lista de mensajes de error de validación.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__(", ".join(errors))


class KycRejectedError(Exception):
    """El servicio KYC rechazó la verificación (400)."""


class EmailValidationError(Exception):
    """El email no cumple las reglas de validación (422)."""


class NameValidationError(Exception):
    """El nombre no cumple las reglas de validación (422)."""


class RegisterUserUseCase:
    """Caso de uso para registro de usuarios.

    Coordina:
    1. Validación de contraseña (value object).
    2. Validación de teléfono (value object).
    3. Verificación de unicidad (repositorio).
    4. Hashing de contraseña (port).
    5. Verificación KYC (port).
    6. Persistencia (repositorio).
    7. Publicación de evento (port).

    Args:
        user_repository: Puerto de persistencia de usuarios.
        password_hasher: Puerto de hashing de contraseñas.
        kyc_verification: Puerto de verificación KYC.
        event_publisher: Puerto de publicación de eventos.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherPort,
        kyc_verification: KycVerificationPort,
        event_publisher: EventPublisherPort,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._kyc_verification = kyc_verification
        self._event_publisher = event_publisher

    async def execute(self, input_dto: RegisterUserInputDTO) -> RegisterUserOutputDTO:
        """Ejecuta el registro de un nuevo usuario.

        Args:
            input_dto: Datos de registro validados por la capa HTTP.

        Returns:
            RegisterUserOutputDTO con el user_id generado.

        Raises:
            PasswordValidationError: Contraseña no cumple reglas.
            ValueError: Teléfono en formato inválido.
            EmailValidationError: Email excede longitud máxima.
            NameValidationError: Nombre excede longitud máxima.
            DuplicatePhoneError: Teléfono ya registrado.
            KycRejectedError: KYC rechazó la verificación.
        """
        # 1. Validar contraseña
        password_errors = HashedPassword.validate_plain_password(input_dto.password)
        if password_errors:
            raise PasswordValidationError(password_errors)

        # 2. Validar teléfono (lanza ValueError si formato inválido)
        phone = PhoneNumber(input_dto.phone)

        # 3. Validar email (opcional)
        if input_dto.email is not None and len(input_dto.email) > 255:
            raise EmailValidationError("Email must be at most 255 characters")

        # 4. Validar nombre (opcional)
        if input_dto.name is not None and len(input_dto.name) > 100:
            raise NameValidationError("Name must be at most 100 characters")

        # 5. Verificar unicidad de teléfono
        existing = await self._user_repository.find_by_phone(phone.value)
        if existing is not None:
            raise DuplicatePhoneError("Phone number already registered")

        # 6. Hash de contraseña
        hashed = self._password_hasher.hash_password(input_dto.password)

        # 7. Verificación KYC
        kyc_status: KycStatus = await self._kyc_verification.verify(phone.value)
        if kyc_status == KycStatus.REJECTED:
            raise KycRejectedError("KYC verification rejected for this phone number")

        # 8. Crear entidad User
        user = User(
            phone=phone.value,
            password_hash=hashed,
            kyc_status=kyc_status,
            email=input_dto.email,
            name=input_dto.name,
        )

        # 9. Persistir
        user_id = await self._user_repository.save(user)

        # 10. Publicar evento
        await self._event_publisher.publish(
            "UserRegistered",
            {"user_id": user_id, "phone": phone.value, "kyc_status": kyc_status.value},
        )

        return RegisterUserOutputDTO(user_id=user_id)
