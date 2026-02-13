"""
Fixtures compartidas para los tests del backend.
"""

from typing import AsyncIterator
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.infrastructure.api.app import create_app


@pytest_asyncio.fixture
async def app() -> AsyncIterator[FastAPI]:
    """Crea una instancia de la aplicación para testing.

    Yields:
        Instancia de FastAPI con MongoDB mockeado.
    """
    with patch("app.infrastructure.api.app.connect_mongo", new_callable=AsyncMock):
        with patch("app.infrastructure.api.app.disconnect_mongo", new_callable=AsyncMock):
            application = create_app()
            async with application.router.lifespan_context(application):
                yield application


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Crea un cliente HTTP asíncrono para testing.

    Args:
        app: Instancia de FastAPI.

    Yields:
        Cliente HTTP asíncrono configurado.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
