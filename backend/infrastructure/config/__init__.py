"""
Configuración de la aplicación.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    app_name: str = "Backend Hexagonal"
    app_version: str = "0.1.0"
    debug: bool = True
    api_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
