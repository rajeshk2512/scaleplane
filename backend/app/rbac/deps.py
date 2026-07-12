from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_token
from app.models import Organization, OrganizationMember, User
from app.rbac.permissions import Permission, role_has_permission

security = HTTPBearer()


@dataclass
class AuthContext:
    user: User
    organization: Organization
    membership: OrganizationMember


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_auth_context(
    user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthContext:
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.user_id == user.id)
        .options(selectinload(OrganizationMember.organization))
        .order_by(OrganizationMember.created_at)
    )
    membership = result.scalars().first()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization membership")

    return AuthContext(user=user, organization=membership.organization, membership=membership)


def require_permission(permission: Permission):
    async def checker(ctx: Annotated[AuthContext, Depends(get_auth_context)]) -> AuthContext:
        if not role_has_permission(ctx.membership.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission.value}",
            )
        return ctx

    return checker
