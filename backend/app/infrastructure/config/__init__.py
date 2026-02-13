"""
Configuración de la aplicación (legacy).

La configuración canónica se encuentra en app.config.settings.
Este módulo re-exporta para compatibilidad.
"""

from app.config.settings import Settings, settings

__all__ = ["Settings", "settings"]
