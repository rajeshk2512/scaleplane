from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import issue_tokens
from app.models import OrganizationMember, Role, User
from app.rbac.deps import AuthContext, get_current_user, require_permission
from app.rbac.permissions import Permission
from app.schemas import (
    MemberCreate,
    MemberResponse,
    MemberUpdate,
    OrganizationCreate,
    OrganizationCreateResponse,
    OrganizationResponse,
    OrganizationUpdate,
    OrganizationWithRoleResponse,
    TokenResponse,
)
from app.services import add_member, create_organization, list_user_organizations, update_organization

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _org_with_role(org, role: Role) -> OrganizationWithRoleResponse:
    return OrganizationWithRoleResponse(
        id=org.id,
        slug=org.slug,
        name=org.name,
        is_default=org.is_default,
        created_at=org.created_at,
        role=role,
    )


@router.post("", response_model=OrganizationCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_org(
    data: OrganizationCreate,
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        org, membership = await create_organization(db, user, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    org_id = str(org.id)
    access_token, refresh_token = issue_tokens(str(user.id), org_id)
    return OrganizationCreateResponse(
        organization=_org_with_role(org, membership.role),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            organization_id=org.id,
        ),
    )


@router.get("", response_model=list[OrganizationWithRoleResponse])
async def list_orgs(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    orgs = await list_user_organizations(db, user)
    return [_org_with_role(org, role) for org, role in orgs]


@router.get("/current", response_model=OrganizationResponse)
async def get_current_org(ctx: Annotated[AuthContext, Depends(require_permission(Permission.org_read))]):
    return ctx.organization


@router.patch("/current", response_model=OrganizationResponse)
async def patch_current_org(
    data: OrganizationUpdate,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.org_update))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        return await update_organization(db, ctx, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/current/members", response_model=list[MemberResponse])
async def list_members(
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.org_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == ctx.organization.id)
        .options(selectinload(OrganizationMember.user))
        .order_by(OrganizationMember.created_at)
    )
    members = result.scalars().all()
    return [
        MemberResponse(
            id=m.id,
            user_id=m.user_id,
            email=m.user.email,
            full_name=m.user.full_name,
            role=m.role,
            created_at=m.created_at,
        )
        for m in members
    ]


@router.post("/current/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    data: MemberCreate,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.org_manage_members))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        member = await add_member(db, ctx, data)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    await db.refresh(member, ["user"])
    return MemberResponse(
        id=member.id,
        user_id=member.user_id,
        email=member.user.email,
        full_name=member.user.full_name,
        role=member.role,
        created_at=member.created_at,
    )


@router.patch("/current/members/{user_id}", response_model=MemberResponse)
async def update_member(
    user_id: UUID,
    data: MemberUpdate,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.org_manage_members))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    if data.role == Role.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot assign owner role")

    result = await db.execute(
        select(OrganizationMember)
        .where(
            OrganizationMember.organization_id == ctx.organization.id,
            OrganizationMember.user_id == user_id,
        )
        .options(selectinload(OrganizationMember.user))
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == Role.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change owner role")

    member.role = data.role
    await db.flush()
    return MemberResponse(
        id=member.id,
        user_id=member.user_id,
        email=member.user.email,
        full_name=member.user.full_name,
        role=member.role,
        created_at=member.created_at,
    )


@router.delete("/current/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    user_id: UUID,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.org_manage_members))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == ctx.organization.id,
            OrganizationMember.user_id == user_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    if member.role == Role.owner:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove owner")
    if member.user_id == ctx.user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove yourself")

    await db.delete(member)
