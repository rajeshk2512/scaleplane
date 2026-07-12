import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
async def _dispose_engine():
    await engine.dispose()
    yield
    await engine.dispose()


@pytest.fixture
async def client():
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

