from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClientConfig:
    base_url: str
    timeout: float = 30.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))
