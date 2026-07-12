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


@dataclass
class TokenPayload:
    user: User
    org_id: UUID | None


async def get_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenPayload:
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

    org_id_raw = payload.get("org_id")
    org_id = UUID(org_id_raw) if org_id_raw else None
    return TokenPayload(user=user, org_id=org_id)


async def get_current_user(
    token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
) -> User:
    return token_payload.user


async def get_auth_context(
    token_payload: Annotated[TokenPayload, Depends(get_token_payload)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthContext:
    if not token_payload.org_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No active organization")

    result = await db.execute(
        select(OrganizationMember)
        .where(
            OrganizationMember.user_id == token_payload.user.id,
            OrganizationMember.organization_id == token_payload.org_id,
        )
        .options(selectinload(OrganizationMember.organization))
    )
    membership = result.scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No organization membership")

    return AuthContext(
        user=token_payload.user,
        organization=membership.organization,
        membership=membership,
    )


def require_permission(permission: Permission):
    async def checker(ctx: Annotated[AuthContext, Depends(get_auth_context)]) -> AuthContext:
        if not role_has_permission(ctx.membership.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission.value}",
            )
        return ctx

    return checker
