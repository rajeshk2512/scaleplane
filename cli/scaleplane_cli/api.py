import httpx
from rich.console import Console

from scaleplane_cli.config import get_api_url, get_token

console = Console()


class ApiError(Exception):
    pass


def request(method: str, path: str, **kwargs) -> dict | list | None:
    token = get_token()
    if not token:
        console.print("[red]Not authenticated. Run: scaleplane auth login[/red]")
        raise SystemExit(1)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    url = f"{get_api_url()}{path}"

    with httpx.Client(timeout=30.0) as client:
        response = client.request(method, url, headers=headers, **kwargs)

    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except Exception:
            detail = response.text
        if response.status_code == 403 and detail == "No active organization":
            console.print(
                '[red]No active organization. Run: scaleplane orgs create --name "My Org" --slug my-org[/red]'
            )
            raise SystemExit(1)
        raise ApiError(f"{response.status_code}: {detail}")

    if response.status_code == 204:
        return None
    return response.json()
