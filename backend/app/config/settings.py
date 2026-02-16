"""Configuracion centralizada de la aplicacion.

Carga variables de entorno desde archivo .env usando Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion de la aplicacion cargada desde variables de entorno.

    Attributes:
        app_name: Nombre de la aplicacion.
        app_version: Version semantica de la aplicacion.
        debug: Modo de depuracion.
        api_prefix: Prefijo para las rutas de la API.
        mongodb_uri: URI de conexion a MongoDB.
        mongodb_database: Nombre de la base de datos MongoDB.
        jwt_private_key: Clave privada RSA para firmar JWT.
        jwt_public_key: Clave publica RSA para verificar JWT.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "Backend Hexagonal"
    app_version: str = "0.1.0"
    debug: bool = True
    api_prefix: str = "/api/v1"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "billetera_virtual"
    jwt_private_key: str = ""
    jwt_public_key: str = ""


settings = Settings()
