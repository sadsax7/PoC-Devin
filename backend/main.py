"""
Punto de entrada principal de la aplicación.
"""

import uvicorn

from app.infrastructure.api.app import create_app


def main() -> None:
    """Inicia la aplicación FastAPI con Uvicorn."""
    app = create_app()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
