from __future__ import annotations


class ApiError(Exception):
    """HTTP or API error returned by ScalePlane."""

    def __init__(self, status: int, detail: str) -> None:
        self.status = status
        self.detail = detail
        super().__init__(f"{status}: {detail}")


class NotFoundError(ApiError):
    """Resource lookup failed (404 or missing slug match)."""

    def __init__(self, detail: str, status: int = 404) -> None:
        super().__init__(status, detail)
