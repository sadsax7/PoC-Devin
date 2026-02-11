"""
Punto de entrada principal de la aplicación.
"""
from infrastructure.api.app import create_app

def main() -> None:
    """Inicia la aplicación."""
    app = create_app()
    
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
