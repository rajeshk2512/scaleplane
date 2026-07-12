import json
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from scaleplane_cli.main import app

runner = CliRunner()
ORG_ID = "11111111-1111-1111-1111-111111111111"
ORG_ID_2 = "22222222-2222-2222-2222-222222222222"


def _mock_response(status_code: int, payload: dict | list | None = None):
    response = MagicMock()
    response.status_code = status_code
    response.text = json.dumps(payload) if payload is not None else ""
    response.json.return_value = payload
    return response


@patch("scaleplane_cli.main.set_tokens")
@patch("scaleplane_cli.main.httpx.Client")
def test_auth_login_without_org(mock_client_cls, mock_set_tokens):
    client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = client
    client.post.return_value = _mock_response(
        200,
        {
            "access_token": "access",
            "refresh_token": "refresh",
            "organization_id": None,
        },
    )

    result = runner.invoke(app, ["auth", "login", "--email", "a@b.com", "--password", "secret123"])
    assert result.exit_code == 0
    mock_set_tokens.assert_called_once_with("access", "refresh", None)
    assert "No organization active" in result.stdout


@patch("scaleplane_cli.main.set_tokens")
@patch("scaleplane_cli.main.httpx.Client")
def test_auth_login_with_org(mock_client_cls, mock_set_tokens):
    client = MagicMock()
    mock_client_cls.return_value.__enter__.return_value = client
    client.post.return_value = _mock_response(
        200,
        {
            "access_token": "access",
            "refresh_token": "refresh",
            "organization_id": ORG_ID,
        },
    )

    result = runner.invoke(app, ["auth", "login", "--email", "a@b.com", "--password", "secret123"])
    assert result.exit_code == 0
    mock_set_tokens.assert_called_once_with("access", "refresh", ORG_ID)
    assert "Logged in successfully" in result.stdout


@patch("scaleplane_cli.main.get_organization_id", return_value=ORG_ID)
@patch("scaleplane_cli.main.api.request")
def test_orgs_list(mock_request, _mock_org_id):
    mock_request.return_value = [
        {
            "id": ORG_ID,
            "name": "Acme",
            "slug": "acme",
            "role": "owner",
            "is_default": False,
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]

    result = runner.invoke(app, ["orgs", "list"])
    assert result.exit_code == 0
    assert "Acme" in result.stdout
    assert "acme" in result.stdout


@patch("scaleplane_cli.main.set_tokens")
@patch("scaleplane_cli.main.api.request")
def test_orgs_create(mock_request, mock_set_tokens):
    mock_request.return_value = {
        "organization": {
            "id": ORG_ID,
            "name": "Acme Corp",
            "slug": "acme-corp",
            "role": "owner",
            "is_default": False,
            "created_at": "2026-01-01T00:00:00Z",
        },
        "tokens": {
            "access_token": "access",
            "refresh_token": "refresh",
            "organization_id": ORG_ID,
        },
    }

    result = runner.invoke(app, ["orgs", "create", "--name", "Acme Corp", "--slug", "acme-corp"])
    assert result.exit_code == 0
    mock_request.assert_called_once_with(
        "POST",
        "/organizations",
        json={"name": "Acme Corp", "slug": "acme-corp"},
    )
    mock_set_tokens.assert_called_once_with("access", "refresh", ORG_ID)
    assert "Created organization Acme Corp" in result.stdout


@patch("scaleplane_cli.main.set_tokens")
@patch("scaleplane_cli.main.api.request")
def test_orgs_switch_by_slug(mock_request, mock_set_tokens):
    mock_request.side_effect = [
        [
            {
                "id": ORG_ID_2,
                "name": "Beta",
                "slug": "beta",
                "role": "owner",
                "is_default": False,
                "created_at": "2026-01-01T00:00:00Z",
            }
        ],
        {
            "access_token": "access2",
            "refresh_token": "refresh2",
            "organization_id": ORG_ID_2,
        },
        {
            "id": ORG_ID_2,
            "name": "Beta",
            "slug": "beta",
            "is_default": False,
            "created_at": "2026-01-01T00:00:00Z",
        },
    ]

    result = runner.invoke(app, ["orgs", "switch", "beta"])
    assert result.exit_code == 0
    mock_set_tokens.assert_called_once_with("access2", "refresh2", ORG_ID_2)
    assert "Switched to organization Beta" in result.stdout
