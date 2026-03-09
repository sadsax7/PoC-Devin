"""
Adapter: UserRepositoryImpl (MongoDB / Motor).

Implementación del puerto UserRepository usando Motor async.

Referencia: BACKEND-GUIDELINES.md §2.4, §5.1.3
"""

from __future__ import annotations

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.domain.entities.user import KycStatus, User
from app.domain.ports.user_repository import UserRepository


class UserRepositoryImpl(UserRepository):
    """Implementación MongoDB del repositorio de usuarios.

    Args:
        db: Base de datos Motor async.
    """

    COLLECTION = "users"

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection = db[self.COLLECTION]

    async def save(self, user: User) -> str:
        """Persiste un usuario nuevo en MongoDB.

        Args:
            user: Entidad User a guardar.

        Returns:
            ID generado por MongoDB (string).
        """
        doc = user.to_dict()
        result = await self._collection.insert_one(doc)
        return str(result.inserted_id)

    async def find_by_phone(self, phone: str) -> User | None:
        """Busca un usuario por número de teléfono.

        Args:
            phone: Número E.164.

        Returns:
            User si existe, None en caso contrario.
        """
        doc = await self._collection.find_one({"phone": phone})
        return self._doc_to_user(doc) if doc else None

    async def find_by_id(self, user_id: str) -> User | None:
        """Busca un usuario por ObjectId.

        Args:
            user_id: ID del usuario como string.

        Returns:
            User si existe, None en caso contrario.
        """
        doc = await self._collection.find_one({"_id": ObjectId(user_id)})
        return self._doc_to_user(doc) if doc else None

    async def ensure_indexes(self) -> None:
        """Crea índice único sobre phone si no existe."""
        await self._collection.create_index("phone", unique=True)

    @staticmethod
    def _doc_to_user(doc: dict[str, object]) -> User:
        """Convierte un documento MongoDB a entidad User.

        Args:
            doc: Documento raw de MongoDB.

        Returns:
            Entidad User hidratada.
        """
        return User(
            id=str(doc["_id"]),
            phone=str(doc["phone"]),
            password_hash=str(doc["password_hash"]),
            kyc_status=KycStatus(str(doc["kyc_status"])),
            email=str(doc["email"]) if doc.get("email") else None,
            name=str(doc["name"]) if doc.get("name") else None,
            mfa_enabled=bool(doc.get("mfa_enabled", False)),
            created_at=doc["created_at"],  # type: ignore[arg-type]
        )
