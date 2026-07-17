from __future__ import annotations

from scaleplane.auth import AuthProvider, BearerTokenAuth
from scaleplane.config import ClientConfig
from scaleplane.resources.prompts import PromptsResource
from scaleplane.resources.routing import RoutingResource
from scaleplane.transport import HttpTransport


class ScalePlaneClient:
    """Facade: closed core + open resource mounts."""

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:8000/api/v1",
        token: str | None = None,
        auth: AuthProvider | None = None,
        timeout: float = 30.0,
    ) -> None:
        if auth is None:
            if not token:
                raise ValueError("Provide token= or auth=")
            auth = BearerTokenAuth(token)
        self._config = ClientConfig(base_url=base_url, timeout=timeout)
        self._transport = HttpTransport(self._config, auth)
        # Resource registration — add new resources here only
        self.prompts = PromptsResource(self._transport)
        self.routing = RoutingResource(self._transport)
