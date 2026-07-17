from __future__ import annotations

from scaleplane._generated.models import CompletionNotImplementedResponse, CompletionRequest
from scaleplane.transport import HttpTransport


class RoutingResource:
    """Routing / completions. Open for new methods; do not change transport."""

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def completions(
        self,
        request: CompletionRequest | None = None,
        *,
        prompt_id: str | None = None,
        prompt_slug: str | None = None,
        tag: str = "production",
        messages: list[dict] | None = None,
        model: str | None = None,
    ) -> CompletionNotImplementedResponse:
        if request is None:
            request = CompletionRequest(
                prompt_id=prompt_id,
                prompt_slug=prompt_slug,
                tag=tag,
                messages=messages or [],
                model=model,
            )
        data = self._transport.request(
            "POST",
            "/route/completions",
            json=request.model_dump(mode="json", exclude_none=True),
            accept_statuses={501},
        )
        return CompletionNotImplementedResponse.model_validate(data)
