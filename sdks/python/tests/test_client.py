from __future__ import annotations

import json
from uuid import uuid4

import httpx
import pytest
import respx

from scaleplane import ApiError, ScalePlaneClient
from scaleplane.errors import NotFoundError


BASE = "https://api.example.test/api/v1"
PROMPT_ID = str(uuid4())
PROJECT_ID = str(uuid4())
VERSION_ID = str(uuid4())


@pytest.fixture
def client() -> ScalePlaneClient:
    return ScalePlaneClient(base_url=BASE, token="test-token")


@respx.mock
def test_resolve(client: ScalePlaneClient) -> None:
    route = respx.get(f"{BASE}/prompts/{PROMPT_ID}/resolve").mock(
        return_value=httpx.Response(
            200,
            json={
                "prompt_id": PROMPT_ID,
                "prompt_slug": "system",
                "tag": "production",
                "version_id": VERSION_ID,
                "version_number": 2,
                "content": "You are helpful.",
                "content_hash": "abc",
                "metadata": None,
            },
        )
    )
    result = client.prompts.resolve(PROMPT_ID, tag="production")
    assert result.prompt_slug == "system"
    assert result.version_number == 2
    assert result.content == "You are helpful."
    assert route.called
    assert route.calls[0].request.headers["Authorization"] == "Bearer test-token"


@respx.mock
def test_promote(client: ScalePlaneClient) -> None:
    tag_id = str(uuid4())
    respx.put(url__regex=rf"{BASE}/prompts/{PROMPT_ID}/tags/staging").mock(
        return_value=httpx.Response(
            200,
            json={
                "id": tag_id,
                "prompt_id": PROMPT_ID,
                "name": "staging",
                "version_id": VERSION_ID,
                "version_number": 3,
                "promoted_at": "2026-01-01T00:00:00Z",
            },
        )
    )
    result = client.prompts.promote(PROMPT_ID, "staging", version_number=3)
    assert result.name == "staging"
    assert result.version_number == 3


@respx.mock
def test_resolve_by_slug(client: ScalePlaneClient) -> None:
    respx.get(f"{BASE}/projects").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": PROJECT_ID,
                    "organization_id": str(uuid4()),
                    "name": "Demo",
                    "slug": "demo",
                    "description": None,
                    "created_at": "2026-01-01T00:00:00Z",
                }
            ],
        )
    )
    respx.get(f"{BASE}/projects/{PROJECT_ID}/prompts").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": PROMPT_ID,
                    "project_id": PROJECT_ID,
                    "organization_id": str(uuid4()),
                    "name": "System",
                    "slug": "system-prompt",
                    "description": None,
                    "created_at": "2026-01-01T00:00:00Z",
                    "latest_version_number": 1,
                    "production_tag_version": 1,
                    "environment_tags": {"production": 1, "staging": None, "dev": None},
                }
            ],
        )
    )
    respx.get(f"{BASE}/prompts/{PROMPT_ID}/resolve").mock(
        return_value=httpx.Response(
            200,
            json={
                "prompt_id": PROMPT_ID,
                "prompt_slug": "system-prompt",
                "tag": "staging",
                "version_id": VERSION_ID,
                "version_number": 1,
                "content": "hi",
                "content_hash": "x",
                "metadata": None,
            },
        )
    )
    result = client.prompts.resolve_by_slug("demo", "system-prompt", tag="staging")
    assert result.content == "hi"


@respx.mock
def test_resolve_by_slug_not_found(client: ScalePlaneClient) -> None:
    respx.get(f"{BASE}/projects").mock(return_value=httpx.Response(200, json=[]))
    with pytest.raises(NotFoundError, match="Project not found"):
        client.prompts.resolve_by_slug("missing", "system")


@respx.mock
def test_api_error(client: ScalePlaneClient) -> None:
    respx.get(f"{BASE}/prompts/{PROMPT_ID}/resolve").mock(
        return_value=httpx.Response(404, json={"detail": "Tag not found"})
    )
    with pytest.raises(ApiError) as exc:
        client.prompts.resolve(PROMPT_ID)
    assert exc.value.status == 404
    assert "Tag not found" in exc.value.detail


@respx.mock
def test_completions(client: ScalePlaneClient) -> None:
    route = respx.post(f"{BASE}/route/completions").mock(
        return_value=httpx.Response(
            501,
            json={
                "detail": "SLM routing is not enabled in the MVP",
                "message": "Provider routing and completion proxy will be available in a future release.",
                "future_capabilities": ["Dynamic SLM / frontier model routing"],
            },
        )
    )
    result = client.routing.completions(prompt_slug="system", tag="production")
    assert "not enabled" in result.detail
    assert result.future_capabilities
    assert route.called
    body = json.loads(route.calls[0].request.content)
    assert body["prompt_slug"] == "system"
    assert body["tag"] == "production"


def test_requires_token() -> None:
    with pytest.raises(ValueError, match="token"):
        ScalePlaneClient(base_url=BASE)
