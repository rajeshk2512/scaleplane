from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class AuthProvider(Protocol):
    """Extension point for auth strategies (Bearer today; API keys later)."""

    def headers(self) -> dict[str, str]: ...


@dataclass(frozen=True)
class BearerTokenAuth:
    token: str

    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}
