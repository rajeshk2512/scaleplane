from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Provider, RoutingPolicy
from app.rbac.deps import AuthContext, require_permission
from app.rbac.permissions import Permission
from app.schemas import (
    CompletionNotImplementedResponse,
    CompletionRequest,
    ProviderCreate,
    ProviderResponse,
    RoutingPolicyCreate,
    RoutingPolicyResponse,
)
from app.services.routing.router import get_router

router = APIRouter(tags=["routing"])


@router.get("/providers", response_model=list[ProviderResponse])
async def list_providers(
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.provider_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(Provider)
        .where(Provider.organization_id == ctx.organization.id)
        .order_by(Provider.created_at.desc())
    )
    return result.scalars().all()


@router.post("/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    data: ProviderCreate,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.provider_write))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing = await db.execute(
        select(Provider).where(
            Provider.organization_id == ctx.organization.id,
            Provider.name == data.name,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider name already exists")

    provider = Provider(
        organization_id=ctx.organization.id,
        name=data.name,
        provider_type=data.provider_type,
        config=data.config,
        is_active=data.is_active,
    )
    db.add(provider)
    await db.flush()
    return provider


@router.get("/routing-policies", response_model=list[RoutingPolicyResponse])
async def list_routing_policies(
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.routing_read))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    result = await db.execute(
        select(RoutingPolicy)
        .where(RoutingPolicy.organization_id == ctx.organization.id)
        .order_by(RoutingPolicy.created_at.desc())
    )
    return result.scalars().all()


@router.post(
    "/routing-policies",
    response_model=RoutingPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_routing_policy(
    data: RoutingPolicyCreate,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.routing_write))],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    existing = await db.execute(
        select(RoutingPolicy).where(
            RoutingPolicy.organization_id == ctx.organization.id,
            RoutingPolicy.name == data.name,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Policy name already exists")

    policy = RoutingPolicy(
        organization_id=ctx.organization.id,
        name=data.name,
        rules=data.rules,
        is_active=data.is_active,
    )
    db.add(policy)
    await db.flush()
    return policy


@router.post(
    "/route/completions",
    response_model=CompletionNotImplementedResponse,
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
async def route_completions(
    data: CompletionRequest,
    ctx: Annotated[AuthContext, Depends(require_permission(Permission.routing_read))],
):
    router_impl = get_router()
    try:
        await router_impl.route_completion(data)
    except NotImplementedError:
        pass

    return CompletionNotImplementedResponse(
        detail="SLM routing is not enabled in the MVP",
        message="Provider routing and completion proxy will be available in a future release.",
        future_capabilities=[
            "Dynamic SLM / frontier model routing",
            "Provider load balancing (TPM/RPM)",
            "Cost-aware fallback chains",
            "Prompt-tagged resolution at inference time",
        ],
    )
