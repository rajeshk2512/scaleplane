import uuid

import pytest
from httpx import AsyncClient


@pytest.fixture
async def owner_client(client: AsyncClient):
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "owner@scaleplane.dev", "password": "password123"},
    )
    if login.status_code != 200:
        pytest.skip("Seed data not loaded — run: python -m app.seed")
    token = login.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.mark.asyncio
async def test_prompt_versioning_flow(owner_client: AsyncClient):
    slug = f"test-project-{uuid.uuid4().hex[:6]}"
    project = await owner_client.post(
        "/api/v1/projects",
        json={"name": "Test Project", "slug": slug},
    )
    assert project.status_code == 201
    project_id = project.json()["id"]

    prompt_slug = f"greeting-{uuid.uuid4().hex[:6]}"
    prompt = await owner_client.post(
        f"/api/v1/projects/{project_id}/prompts",
        json={
            "name": "Greeting",
            "slug": prompt_slug,
            "content": "Hello, {{name}}!",
            "metadata": {"template": True},
        },
    )
    assert prompt.status_code == 201
    prompt_id = prompt.json()["id"]
    assert prompt.json()["latest_version_number"] == 1

    version = await owner_client.post(
        f"/api/v1/prompts/{prompt_id}/versions",
        json={"content": "Hi, {{name}}! Welcome to ScalePlane."},
    )
    assert version.status_code == 201
    assert version.json()["version_number"] == 2

    staging = await owner_client.put(
        f"/api/v1/prompts/{prompt_id}/tags/staging",
        params={"version_number": 2},
    )
    assert staging.status_code == 200
    assert staging.json()["version_number"] == 2

    prompt_detail = await owner_client.get(f"/api/v1/prompts/{prompt_id}")
    assert prompt_detail.status_code == 200
    env_tags = prompt_detail.json()["environment_tags"]
    assert env_tags["staging"] == 2
    assert env_tags["production"] is None
    assert env_tags["dev"] is None

    promote = await owner_client.put(
        f"/api/v1/prompts/{prompt_id}/tags/production",
        params={"version_number": 2},
    )
    assert promote.status_code == 200
    assert promote.json()["version_number"] == 2

    prompt_after_prod = await owner_client.get(f"/api/v1/prompts/{prompt_id}")
    assert prompt_after_prod.json()["environment_tags"]["production"] == 2
    assert prompt_after_prod.json()["environment_tags"]["staging"] == 2

    resolve = await owner_client.get(
        f"/api/v1/prompts/{prompt_id}/resolve",
        params={"tag": "production"},
    )
    assert resolve.status_code == 200
    assert "ScalePlane" in resolve.json()["content"]
