from __future__ import annotations

from typing import Any

import httpx

from scaleplane.auth import AuthProvider
from scaleplane.config import ClientConfig
from scaleplane.errors import ApiError


class HttpTransport:
    """Closed HTTP layer — resources call this; do not extend per feature."""

    def __init__(self, config: ClientConfig, auth: AuthProvider) -> None:
        self._config = config
        self._auth = auth

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        accept_statuses: set[int] | None = None,
    ) -> Any:
        url = f"{self._config.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **self._auth.headers(),
        }
        with httpx.Client(timeout=self._config.timeout) as client:
            response = client.request(method, url, headers=headers, params=params, json=json)

        ok = response.status_code < 400 or (
            accept_statuses is not None and response.status_code in accept_statuses
        )
        if not ok:
            detail = _extract_detail(response)
            raise ApiError(response.status_code, detail)

        if response.status_code == 204 or not response.content:
            return None
        return response.json()


def _extract_detail(response: httpx.Response) -> str:
    try:
        body = response.json()
        if isinstance(body, dict) and "detail" in body:
            detail = body["detail"]
            return detail if isinstance(detail, str) else str(detail)
    except Exception:
        pass
    return response.text or response.reason_phrase
