"""
Cliente asíncrono de MongoDB usando Motor.

Provee funciones de ciclo de vida para conectar y desconectar
el cliente Motor, y una función para verificar conectividad.
"""

from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: Optional[AsyncIOMotorClient] = None  # type: ignore[type-arg]
_database: Optional[AsyncIOMotorDatabase] = None  # type: ignore[type-arg]


async def connect_mongo(uri: str, database_name: str) -> None:
    """Establece la conexión asíncrona a MongoDB.

    Args:
        uri: URI de conexión a MongoDB.
        database_name: Nombre de la base de datos a utilizar.
    """
    global _client, _database
    _client = AsyncIOMotorClient(uri)
    _database = _client[database_name]


async def disconnect_mongo() -> None:
    """Cierra la conexión a MongoDB de forma segura."""
    global _client, _database
    if _client is not None:
        _client.close()
    _client = None
    _database = None


def get_database() -> AsyncIOMotorDatabase:  # type: ignore[type-arg]
    """Retorna la instancia de la base de datos MongoDB.

    Returns:
        Instancia de AsyncIOMotorDatabase.

    Raises:
        RuntimeError: Si la conexión no ha sido establecida.
    """
    if _database is None:
        raise RuntimeError("MongoDB no está conectado. Llama a connect_mongo primero.")
    return _database


async def ping_mongo() -> bool:
    """Verifica conectividad con MongoDB ejecutando un comando ping.

    Returns:
        True si el ping fue exitoso, False en caso contrario.
    """
    if _client is None:
        return False
    try:
        result = await _client.admin.command("ping")
        return bool(result.get("ok", 0) == 1.0)
    except Exception:
        return False
