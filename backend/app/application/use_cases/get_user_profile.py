"""
Caso de uso: Obtener perfil del usuario autenticado.

Busca el usuario por su identificador único y retorna sus datos
sanitizados (sin password_hash ni campos sensibles).
Cumple HU-BE-03 AC#2 y AC#3.

Referencia: BACKEND-GUIDELINES.md §5.1.2, §5.1.3, HU-BE-03.
"""

from __future__ import annotations

from app.application.dtos.user_profile_dto import UserProfileOutputDTO
from app.domain.ports.user_repository import UserRepository


class UserProfileNotFoundError(Exception):
    """El usuario no existe en la base de datos.

    Puede ocurrir si el usuario fue eliminado después de emitir
    el JWT (HU-BE-03 AC#2 — caso edge).
    """


class GetUserProfileUseCase:
    """Recupera y sanitiza el perfil del usuario autenticado.

    Attributes:
        _user_repository: Repositorio de usuarios via port.
    """

    def __init__(self, *, user_repository: UserRepository) -> None:
        """Inicializa el caso de uso con sus dependencias.

        Args:
            user_repository: Puerto de acceso al repositorio de usuarios.
        """
        self._user_repository = user_repository

    async def execute(self, user_id: str) -> UserProfileOutputDTO:
        """Obtiene el perfil sanitizado del usuario por su ID.

        Args:
            user_id: Identificador único del usuario (sub del JWT).

        Returns:
            DTO con los datos públicos del usuario.

        Raises:
            UserProfileNotFoundError: Si no existe usuario con ese ID.
        """
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserProfileNotFoundError(f"User with id '{user_id}' not found")

        created_at_iso = user.created_at.isoformat().replace("+00:00", "Z")
        if not created_at_iso.endswith("Z"):
            created_at_iso = created_at_iso + "Z"

        return UserProfileOutputDTO(
            user_id=user_id,
            phone=user.phone,
            email=user.email,
            name=user.name,
            kyc_status=user.kyc_status.value,
            mfa_enabled=user.mfa_enabled,
            created_at=created_at_iso,
        )
