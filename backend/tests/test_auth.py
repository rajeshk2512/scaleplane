import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_docs(client: AsyncClient):
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    email = f"testuser-{uuid.uuid4().hex[:8]}@example.com"
    password = "securepass123"

    register = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert register.status_code == 201
    assert register.json()["email"] == email

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    tokens = login.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = await client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == email

    org = await client.get("/api/v1/organizations/current", headers=headers)
    assert org.status_code == 200
    assert org.json()["slug"] == "default"
