from typing import Protocol

from app.schemas import CompletionRequest


class CompletionResponse:
    def __init__(self, content: str, model: str, provider: str):
        self.content = content
        self.model = model
        self.provider = provider


class RouterPort(Protocol):
    async def route_completion(self, request: CompletionRequest) -> CompletionResponse: ...


class NoOpRouter:
    async def route_completion(self, request: CompletionRequest) -> CompletionResponse:
        raise NotImplementedError("SLM routing not enabled in MVP")


def get_router() -> RouterPort:
    return NoOpRouter()
