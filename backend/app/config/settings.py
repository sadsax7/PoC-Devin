"""
Configuración centralizada de la aplicación.

Carga variables de entorno desde archivo .env usando Pydantic Settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno.

    Attributes:
        app_name: Nombre de la aplicación.
        app_version: Versión semántica de la aplicación.
        debug: Modo de depuración.
        api_prefix: Prefijo para las rutas de la API.
        mongodb_uri: URI de conexión a MongoDB.
        mongodb_database: Nombre de la base de datos MongoDB.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "Backend Hexagonal"
    app_version: str = "0.1.0"
    debug: bool = True
    api_prefix: str = "/api/v1"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "billetera_virtual"


settings = Settings()
