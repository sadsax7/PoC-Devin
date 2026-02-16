"""Fixtures compartidas para los tests del backend."""

from typing import AsyncIterator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.infrastructure.api.app import create_app


@pytest_asyncio.fixture
async def app() -> AsyncIterator[FastAPI]:
    """Crea una instancia de la aplicacion para testing.

    Yields:
        Instancia de FastAPI con MongoDB mockeado.
    """
    with patch("app.infrastructure.api.app.connect_mongo", new_callable=AsyncMock):
        with patch("app.infrastructure.api.app.disconnect_mongo", new_callable=AsyncMock):
            with patch("app.infrastructure.api.app.get_database") as mock_db:
                mock_db.return_value = MagicMock()
                with patch("app.infrastructure.api.app.MongoUserRepository") as mock_repo_cls:
                    mock_repo_cls.return_value.ensure_indexes = AsyncMock()
                    application = create_app()
                    async with application.router.lifespan_context(application):
                        yield application


@pytest_asyncio.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    """Crea un cliente HTTP asincrono para testing.

    Args:
        app: Instancia de FastAPI.

    Yields:
        Cliente HTTP asincrono configurado.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
