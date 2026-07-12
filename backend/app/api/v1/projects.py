from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Project
from app.rbac.deps import AuthContext, require_permission
from app.rbac.permissions import Permission
from app.schemas import ProjectCreate, ProjectResponse
from app.services import create_project

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.project_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Project)
        .where(Project.organization_id == ctx.organization.id)
        .order_by(Project.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    data: ProjectCreate,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.project_write))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing = await db.execute(
        select(Project).where(
            Project.organization_id == ctx.organization.id,
            Project.slug == data.slug,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project slug already exists")

    return await create_project(db, ctx, data)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.project_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    project = await db.get(Project, project_id)
    if not project or project.organization_id != ctx.organization.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project
