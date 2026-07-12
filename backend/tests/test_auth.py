import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_docs(client: AsyncClient):
    response = await client.get("/docs")
    assert response.status_code == 200
