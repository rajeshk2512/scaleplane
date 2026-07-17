from __future__ import annotations

from uuid import UUID

from scaleplane._generated.models import (
    ProjectResponse,
    PromptResolveResponse,
    PromptResponse,
    PromptTagResponse,
)
from scaleplane.errors import NotFoundError
from scaleplane.transport import HttpTransport


class PromptsResource:
    """Runtime prompt resolve / promote. Open for new methods; do not change transport."""

    def __init__(self, transport: HttpTransport) -> None:
        self._transport = transport

    def resolve(self, prompt_id: str | UUID, *, tag: str = "production") -> PromptResolveResponse:
        data = self._transport.request(
            "GET",
            f"/prompts/{prompt_id}/resolve",
            params={"tag": tag},
        )
        return PromptResolveResponse.model_validate(data)

    def promote(
        self,
        prompt_id: str | UUID,
        tag: str,
        *,
        version_number: int | None = None,
        version_id: str | UUID | None = None,
    ) -> PromptTagResponse:
        params: dict[str, str | int] = {}
        if version_number is not None:
            params["version_number"] = version_number
        if version_id is not None:
            params["version_id"] = str(version_id)
        data = self._transport.request(
            "PUT",
            f"/prompts/{prompt_id}/tags/{tag}",
            params=params or None,
        )
        return PromptTagResponse.model_validate(data)

    def resolve_by_slug(
        self,
        project: str,
        prompt: str,
        *,
        tag: str = "production",
    ) -> PromptResolveResponse:
        """Resolve by project/prompt slug (extra RTT for lookups)."""
        prompt_id = self._lookup_prompt_id(project, prompt)
        return self.resolve(prompt_id, tag=tag)

    def promote_by_slug(
        self,
        project: str,
        prompt: str,
        tag: str,
        *,
        version_number: int | None = None,
        version_id: str | UUID | None = None,
    ) -> PromptTagResponse:
        """Promote by project/prompt slug (extra RTT for lookups)."""
        prompt_id = self._lookup_prompt_id(project, prompt)
        return self.promote(
            prompt_id,
            tag,
            version_number=version_number,
            version_id=version_id,
        )

    def _lookup_prompt_id(self, project: str, prompt_slug: str) -> UUID:
        project_id = self._lookup_project_id(project)
        prompts_data = self._transport.request("GET", f"/projects/{project_id}/prompts")
        prompts = [PromptResponse.model_validate(p) for p in prompts_data]
        for p in prompts:
            if p.slug == prompt_slug or str(p.id) == prompt_slug:
                return p.id
        raise NotFoundError(f"Prompt not found: {prompt_slug}")

    def _lookup_project_id(self, project: str) -> UUID:
        projects_data = self._transport.request("GET", "/projects")
        projects = [ProjectResponse.model_validate(p) for p in projects_data]
        for p in projects:
            if p.slug == project or str(p.id) == project:
                return p.id
        raise NotFoundError(f"Project not found: {project}")
