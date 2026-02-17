"""Caso de uso para obtener el perfil del usuario autenticado.

Orquesta la consulta del perfil de usuario a partir del ID
extraido del token JWT, sanitizando la respuesta.
"""

from datetime import timezone

from app.application.dtos.user_profile_dto import UserProfileInputDTO, UserProfileOutputDTO
from app.domain.ports.user_repository import UserRepositoryPort


class UserNotFoundError(Exception):
    """Error cuando el usuario no se encuentra en la base de datos."""


class GetUserProfileUseCase:
    """Caso de uso para consultar el perfil de un usuario autenticado.

    Busca al usuario por ID y retorna una respuesta sanitizada
    sin campos sensibles como password_hash o mfa_secret.
    """

    def __init__(self, user_repository: UserRepositoryPort) -> None:
        """Inicializa el caso de uso con sus dependencias.

        Args:
            user_repository: Puerto del repositorio de usuarios.
        """
        self._user_repository = user_repository

    async def execute(self, input_dto: UserProfileInputDTO) -> UserProfileOutputDTO:
        """Ejecuta la consulta del perfil de usuario.

        Args:
            input_dto: DTO con el user_id del usuario autenticado.

        Returns:
            DTO con los datos sanitizados del perfil.

        Raises:
            UserNotFoundError: Si el usuario no existe en la base de datos.
        """
        user = await self._user_repository.find_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError("User not found")

        # Asegurar que created_at este en UTC antes de formatear con sufijo 'Z'
        if user.created_at.tzinfo is None:
            created_at_utc = user.created_at.replace(tzinfo=timezone.utc)
        else:
            created_at_utc = user.created_at.astimezone(timezone.utc)

        created_at_str = (
            created_at_utc.strftime("%Y-%m-%dT%H:%M:%S.") + created_at_utc.strftime("%f")[:3] + "Z"
        )

        return UserProfileOutputDTO(
            user_id=user.id or "",
            phone=user.phone,
            email=user.email,
            name=user.name,
            kyc_status=user.kyc_status,
            mfa_enabled=user.mfa_enabled,
            created_at=created_at_str,
        )
