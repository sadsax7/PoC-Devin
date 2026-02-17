"""
Configuración de la aplicación.

Gestiona settings via variables de entorno (.env) usando Pydantic Settings.
Incluye configuración de MongoDB, JWT, KYC y parámetros generales.

Referencia: BACKEND-GUIDELINES.md §2, HU-BE-00 Acceptance Criteria #3
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración central de la aplicación.

    Carga valores desde variables de entorno o archivo .env.
    Ningún secreto debe estar hardcodeado aquí.

    Attributes:
        app_name: Nombre de la aplicación.
        app_version: Versión semántica.
        debug: Modo debug activo/inactivo.
        api_prefix: Prefijo para todas las rutas de API.
        mongodb_uri: URI de conexión a MongoDB.
        mongodb_db_name: Nombre de la base de datos.
        jwt_private_key_path: Ruta a clave privada RSA.
        jwt_public_key_path: Ruta a clave pública RSA.
        jwt_access_token_expire_minutes: Minutos de expiración del access token.
        jwt_refresh_token_expire_days: Días de expiración del refresh token.
        kyc_service_url: URL del servicio KYC externo.
        kyc_mock_enabled: Flag para usar mock de KYC.
    """

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    app_name: str = "Backend Hexagonal"
    app_version: str = "0.1.0"
    debug: bool = True
    api_prefix: str = "/api/v1"

    # MongoDB
    mongodb_uri: str = "mongodb://admin:admin@localhost:27017"
    mongodb_db_name: str = "billetera_db"

    # JWT
    jwt_private_key_path: str = "./keys/private.pem"
    jwt_public_key_path: str = "./keys/public.pem"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # KYC
    kyc_service_url: str = "http://localhost:8081/kyc"
    kyc_mock_enabled: bool = True


settings = Settings()
