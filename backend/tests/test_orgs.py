import uuid

import pytest
from httpx import AsyncClient


async def register_user(client: AsyncClient, email: str | None = None, password: str = "securepass123"):
    email = email or f"testuser-{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert response.status_code == 201
    return email, password, response.json()


async def login_user(client: AsyncClient, email: str, password: str):
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


async def create_org(client: AsyncClient, headers: dict, name: str, slug: str):
    response = await client.post(
        "/api/v1/organizations",
        json={"name": name, "slug": slug},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_register_and_login_flow(client: AsyncClient):
    email, password, _ = await register_user(client)

    tokens = await login_user(client, email, password)
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["organization_id"] is None

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    me = await client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == email

    org = await client.get("/api/v1/organizations/current", headers=headers)
    assert org.status_code == 403
    assert org.json()["detail"] == "No active organization"


@pytest.mark.asyncio
async def test_create_organization_onboarding(client: AsyncClient):
    email, password, _ = await register_user(client)
    tokens = await login_user(client, email, password)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    slug = f"acme-{uuid.uuid4().hex[:6]}"
    created = await create_org(client, headers, "Acme Corp", slug)
    assert created["organization"]["slug"] == slug
    assert created["organization"]["role"] == "owner"
    assert created["tokens"]["organization_id"] == created["organization"]["id"]

    headers = {"Authorization": f"Bearer {created['tokens']['access_token']}"}
    org = await client.get("/api/v1/organizations/current", headers=headers)
    assert org.status_code == 200
    assert org.json()["slug"] == slug


@pytest.mark.asyncio
async def test_login_with_org(client: AsyncClient):
    email, password, _ = await register_user(client)
    tokens = await login_user(client, email, password)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    slug = f"login-org-{uuid.uuid4().hex[:6]}"
    created = await create_org(client, headers, "Login Org", slug)

    tokens = await login_user(client, email, password)
    assert tokens["organization_id"] == created["organization"]["id"]


@pytest.mark.asyncio
async def test_switch_org(client: AsyncClient):
    email, password, _ = await register_user(client)
    tokens = await login_user(client, email, password)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    slug_a = f"org-a-{uuid.uuid4().hex[:6]}"
    slug_b = f"org-b-{uuid.uuid4().hex[:6]}"
    org_a = await create_org(client, headers, "Org A", slug_a)
    headers = {"Authorization": f"Bearer {org_a['tokens']['access_token']}"}
    org_b = await create_org(client, headers, "Org B", slug_b)

    switched = await client.post(
        "/api/v1/auth/switch-org",
        json={"organization_id": org_a["organization"]["id"]},
        headers={"Authorization": f"Bearer {org_b['tokens']['access_token']}"},
    )
    assert switched.status_code == 200
    assert switched.json()["organization_id"] == org_a["organization"]["id"]

    fake_id = str(uuid.uuid4())
    invalid = await client.post(
        "/api/v1/auth/switch-org",
        json={"organization_id": fake_id},
        headers={"Authorization": f"Bearer {switched.json()['access_token']}"},
    )
    assert invalid.status_code == 403


@pytest.mark.asyncio
async def test_list_organizations(client: AsyncClient):
    email, password, _ = await register_user(client)
    tokens = await login_user(client, email, password)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    slug_a = f"list-a-{uuid.uuid4().hex[:6]}"
    slug_b = f"list-b-{uuid.uuid4().hex[:6]}"
    await create_org(client, headers, "List A", slug_a)
    await create_org(client, headers, "List B", slug_b)

    listed = await client.get("/api/v1/organizations", headers=headers)
    assert listed.status_code == 200
    slugs = {org["slug"] for org in listed.json()}
    assert slug_a in slugs
    assert slug_b in slugs
    assert all(org["role"] == "owner" for org in listed.json())


@pytest.mark.asyncio
async def test_update_organization(client: AsyncClient):
    email, password, _ = await register_user(client)
    tokens = await login_user(client, email, password)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    slug = f"update-{uuid.uuid4().hex[:6]}"
    created = await create_org(client, headers, "Old Name", slug)
    headers = {"Authorization": f"Bearer {created['tokens']['access_token']}"}

    updated = await client.patch(
        "/api/v1/organizations/current",
        json={"name": "New Name"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_org_isolation(client: AsyncClient):
    email_a, password_a, _ = await register_user(client)
    tokens_a = await login_user(client, email_a, password_a)
    headers_a = {"Authorization": f"Bearer {tokens_a['access_token']}"}
    slug_a = f"iso-a-{uuid.uuid4().hex[:6]}"
    org_a = await create_org(client, headers_a, "Iso A", slug_a)
    headers_a = {"Authorization": f"Bearer {org_a['tokens']['access_token']}"}

    project = await client.post(
        "/api/v1/projects",
        json={"name": "Secret Project", "slug": f"secret-{uuid.uuid4().hex[:6]}"},
        headers=headers_a,
    )
    assert project.status_code == 201
    project_id = project.json()["id"]

    email_b, password_b, _ = await register_user(client)
    tokens_b = await login_user(client, email_b, password_b)
    headers_b = {"Authorization": f"Bearer {tokens_b['access_token']}"}
    slug_b = f"iso-b-{uuid.uuid4().hex[:6]}"
    org_b = await create_org(client, headers_b, "Iso B", slug_b)
    headers_b = {"Authorization": f"Bearer {org_b['tokens']['access_token']}"}

    switched = await client.post(
        "/api/v1/auth/switch-org",
        json={"organization_id": org_a["organization"]["id"]},
        headers=headers_b,
    )
    assert switched.status_code == 403

    leaked = await client.get(f"/api/v1/projects/{project_id}", headers=headers_b)
    assert leaked.status_code in (403, 404)
