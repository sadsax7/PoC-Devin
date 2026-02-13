"""
Punto de entrada principal de la aplicación.
"""

import uvicorn


def main() -> None:
    """Inicia la aplicación FastAPI con Uvicorn."""
    # When using reload/workers, pass the application as an import string
    # and set factory=True if the target is a factory callable.
    uvicorn.run(
        "app.infrastructure.api.app:create_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        factory=True,
    )


if __name__ == "__main__":
    main()
