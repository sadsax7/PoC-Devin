"""Implementacion MongoDB del repositorio de usuarios.

Adaptador de salida que implementa el puerto UserRepositoryPort
usando Motor (driver asincrono de MongoDB).
"""

from datetime import timezone
from typing import Any, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities.user import User
from app.domain.ports.user_repository import UserRepositoryPort


class MongoUserRepository(UserRepositoryPort):
    """Repositorio de usuarios con persistencia en MongoDB.

    Almacena documentos de usuario en la coleccion 'users'
    y gestiona el indice unico en el campo 'phone'.
    """

    COLLECTION_NAME = "users"

    def __init__(self, database: AsyncIOMotorDatabase) -> None:  # type: ignore[type-arg]
        """Inicializa el repositorio con la base de datos MongoDB.

        Args:
            database: Instancia de la base de datos MongoDB.
        """
        self._collection = database[self.COLLECTION_NAME]

    async def ensure_indexes(self) -> None:
        """Crea indices necesarios en la coleccion si no existen."""
        await self._collection.create_index("phone", unique=True)

    async def find_by_phone(self, phone: str) -> Optional[User]:
        """Busca un usuario por numero de telefono.

        Args:
            phone: Numero de telefono en formato E.164.

        Returns:
            User si existe, None en caso contrario.
        """
        doc = await self._collection.find_one({"phone": phone})
        if doc is None:
            return None
        return self._doc_to_user(doc)

    async def create(self, user: User) -> User:
        """Crea un nuevo usuario en MongoDB.

        Args:
            user: Entidad User a persistir.

        Returns:
            User con identificador ObjectId asignado.
        """
        doc = self._user_to_doc(user)
        result = await self._collection.insert_one(doc)
        user.id = str(result.inserted_id)
        return user

    @staticmethod
    def _user_to_doc(user: User) -> dict[str, Any]:
        """Convierte una entidad User a documento MongoDB.

        Args:
            user: Entidad User a convertir.

        Returns:
            Diccionario representando el documento MongoDB.
        """
        return {
            "phone": user.phone,
            "email": user.email,
            "name": user.name,
            "password_hash": user.password_hash,
            "kyc_status": user.kyc_status,
            "mfa_enabled": user.mfa_enabled,
            "created_at": user.created_at,
        }

    @staticmethod
    def _doc_to_user(doc: dict[str, Any]) -> User:
        """Convierte un documento MongoDB a entidad User.

        Args:
            doc: Documento MongoDB.

        Returns:
            Entidad User reconstruida.
        """
        created_at = doc["created_at"]
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        return User(
            id=str(doc["_id"]),
            phone=doc["phone"],
            email=doc.get("email"),
            name=doc.get("name"),
            password_hash=doc["password_hash"],
            kyc_status=doc["kyc_status"],
            mfa_enabled=doc["mfa_enabled"],
            created_at=created_at,
        )
