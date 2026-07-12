from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models import Project, Prompt, PromptTag, PromptVersion
from app.rbac.deps import AuthContext, require_permission
from app.rbac.permissions import Permission
from app.schemas import (
    ENVIRONMENT_TAGS,
    PromptCreate,
    PromptEnvironmentTags,
    PromptResolveResponse,
    PromptResponse,
    PromptTagResponse,
    PromptVersionCreate,
    PromptVersionResponse,
)
from app.services import create_prompt, create_prompt_version, promote_tag, resolve_prompt

router = APIRouter(tags=["prompts"])


async def _get_prompt_response(db: AsyncSession, prompt: Prompt) -> PromptResponse:
    latest = await db.scalar(
        select(func.max(PromptVersion.version_number)).where(PromptVersion.prompt_id == prompt.id)
    )
    tag_result = await db.execute(
        select(PromptTag)
        .where(PromptTag.prompt_id == prompt.id, PromptTag.name.in_(ENVIRONMENT_TAGS))
        .options(selectinload(PromptTag.version))
    )
    tag_versions = {
        tag.name: tag.version.version_number
        for tag in tag_result.scalars().all()
    }
    environment_tags = PromptEnvironmentTags(
        production=tag_versions.get("production"),
        staging=tag_versions.get("staging"),
        dev=tag_versions.get("dev"),
    )
    return PromptResponse(
        id=prompt.id,
        project_id=prompt.project_id,
        organization_id=prompt.organization_id,
        name=prompt.name,
        slug=prompt.slug,
        description=prompt.description,
        created_at=prompt.created_at,
        latest_version_number=latest,
        production_tag_version=environment_tags.production,
        environment_tags=environment_tags,
    )


@router.get("/projects/{project_id}/prompts", response_model=list[PromptResponse])
async def list_prompts(
    project_id: UUID,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.prompt_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await db.get(Project, project_id)
    if not project or project.organization_id != ctx.organization.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    result = await db.execute(
        select(Prompt).where(Prompt.project_id == project_id).order_by(Prompt.created_at.desc())
    )
    prompts = result.scalars().all()
    return [await _get_prompt_response(db, p) for p in prompts]


@router.post(
    "/projects/{project_id}/prompts",
    response_model=PromptResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_prompt_endpoint(
    project_id: UUID,
    data: PromptCreate,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.prompt_write))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing = await db.execute(
        select(Prompt).where(Prompt.project_id == project_id, Prompt.slug == data.slug)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Prompt slug already exists")

    try:
        prompt, _ = await create_prompt(db, ctx, project_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return await _get_prompt_response(db, prompt)


@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
async def get_prompt(
    prompt_id: UUID,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.prompt_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    prompt = await db.get(Prompt, prompt_id)
    if not prompt or prompt.organization_id != ctx.organization.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return await _get_prompt_response(db, prompt)


@router.post(
    "/prompts/{prompt_id}/versions",
    response_model=PromptVersionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_version(
    prompt_id: UUID,
    data: PromptVersionCreate,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.prompt_write))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        version = await create_prompt_version(db, ctx, prompt_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return PromptVersionResponse(
        id=version.id,
        prompt_id=version.prompt_id,
        version_number=version.version_number,
        content=version.content,
        content_hash=version.content_hash,
        metadata=version.metadata_,
        parent_version_id=version.parent_version_id,
        created_by_id=version.created_by_id,
        created_at=version.created_at,
    )


@router.get("/prompts/{prompt_id}/versions", response_model=list[PromptVersionResponse])
async def list_versions(
    prompt_id: UUID,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.prompt_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    prompt = await db.get(Prompt, prompt_id)
    if not prompt or prompt.organization_id != ctx.organization.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")

    result = await db.execute(
        select(PromptVersion)
        .where(PromptVersion.prompt_id == prompt_id)
        .order_by(PromptVersion.version_number.desc())
    )
    versions = result.scalars().all()
    return [
        PromptVersionResponse(
            id=v.id,
            prompt_id=v.prompt_id,
            version_number=v.version_number,
            content=v.content,
            content_hash=v.content_hash,
            metadata=v.metadata_,
            parent_version_id=v.parent_version_id,
            created_by_id=v.created_by_id,
            created_at=v.created_at,
        )
        for v in versions
    ]


@router.get("/prompts/{prompt_id}/versions/{version_id}", response_model=PromptVersionResponse)
async def get_version(
    prompt_id: UUID,
    version_id: UUID,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.prompt_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    version = await db.get(PromptVersion, version_id)
    if not version or version.prompt_id != prompt_id or version.organization_id != ctx.organization.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")

    return PromptVersionResponse(
        id=version.id,
        prompt_id=version.prompt_id,
        version_number=version.version_number,
        content=version.content,
        content_hash=version.content_hash,
        metadata=version.metadata_,
        parent_version_id=version.parent_version_id,
        created_by_id=version.created_by_id,
        created_at=version.created_at,
    )


@router.put("/prompts/{prompt_id}/tags/{tag_name}", response_model=PromptTagResponse)
async def promote_prompt_tag(
    prompt_id: UUID,
    tag_name: str,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.prompt_promote))],
    db: Annotated[AsyncSession, Depends(get_db)],
    version_id: UUID | None = None,
    version_number: int | None = Query(default=None),
):
    try:
        tag = await promote_tag(db, ctx, prompt_id, tag_name, version_id, version_number)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    version = await db.get(PromptVersion, tag.version_id)
    return PromptTagResponse(
        id=tag.id,
        prompt_id=tag.prompt_id,
        name=tag.name,
        version_id=tag.version_id,
        version_number=version.version_number if version else 0,
        promoted_at=tag.promoted_at,
    )


@router.get("/prompts/{prompt_id}/resolve", response_model=PromptResolveResponse)
async def resolve_prompt_endpoint(
    prompt_id: UUID,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.prompt_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
    tag: str = Query(default="production"),
):
    try:
        prompt, version, prompt_tag = await resolve_prompt(db, ctx, prompt_id, tag)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return PromptResolveResponse(
        prompt_id=prompt.id,
        prompt_slug=prompt.slug,
        tag=prompt_tag.name,
        version_id=version.id,
        version_number=version.version_number,
        content=version.content,
        content_hash=version.content_hash,
        metadata=version.metadata_,
    )
