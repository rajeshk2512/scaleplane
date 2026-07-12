import hashlib
import re
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.security import hash_password
from app.models import (
    Organization,
    OrganizationMember,
    Project,
    Prompt,
    PromptTag,
    PromptVersion,
    Role,
    User,
)
from app.rbac.deps import AuthContext
from app.schemas import (
    MemberCreate,
    MemberUpdate,
    ProjectCreate,
    PromptCreate,
    PromptVersionCreate,
    UserRegister,
)


async def ensure_default_organization(db: AsyncSession) -> Organization:
    settings = get_settings()
    result = await db.execute(
        select(Organization).where(Organization.slug == settings.default_org_slug)
    )
    org = result.scalar_one_or_none()
    if org:
        return org

    org = Organization(
        slug=settings.default_org_slug,
        name=settings.default_org_name,
        is_default=True,
    )
    db.add(org)
    await db.flush()
    return org


async def register_user(db: AsyncSession, data: UserRegister) -> User:
    existing = await db.execute(select(User).where(User.email == data.email.lower()))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    org = await ensure_default_organization(db)
    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.flush()

    member_count = await db.scalar(
        select(func.count()).select_from(OrganizationMember).where(
            OrganizationMember.organization_id == org.id
        )
    )
    role = Role.owner if member_count == 0 else Role.viewer

    db.add(
        OrganizationMember(
            user_id=user.id,
            organization_id=org.id,
            role=role,
        )
    )
    await db.flush()
    return user


async def add_member(db: AsyncSession, ctx: AuthContext, data: MemberCreate) -> OrganizationMember:
    result = await db.execute(select(User).where(User.email == data.email.lower()))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("User not found. They must register first.")

    existing = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.organization_id == ctx.organization.id,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("User is already a member")

    if data.role == Role.owner:
        raise ValueError("Cannot assign owner role via API")

    member = OrganizationMember(
        user_id=user.id,
        organization_id=ctx.organization.id,
        role=data.role,
    )
    db.add(member)
    await db.flush()
    return member


async def create_project(db: AsyncSession, ctx: AuthContext, data: ProjectCreate) -> Project:
    project = Project(
        organization_id=ctx.organization.id,
        name=data.name,
        slug=data.slug,
        description=data.description,
    )
    db.add(project)
    await db.flush()
    return project


def content_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def create_prompt(
    db: AsyncSession, ctx: AuthContext, project_id: UUID, data: PromptCreate
) -> tuple[Prompt, PromptVersion]:
    project = await db.get(Project, project_id)
    if not project or project.organization_id != ctx.organization.id:
        raise ValueError("Project not found")

    prompt = Prompt(
        project_id=project.id,
        organization_id=ctx.organization.id,
        name=data.name,
        slug=data.slug,
        description=data.description,
    )
    db.add(prompt)
    await db.flush()

    version = PromptVersion(
        prompt_id=prompt.id,
        organization_id=ctx.organization.id,
        version_number=1,
        content=data.content,
        content_hash=content_hash(data.content),
        metadata_=data.metadata,
        created_by_id=ctx.user.id,
    )
    db.add(version)
    await db.flush()
    return prompt, version


async def create_prompt_version(
    db: AsyncSession,
    ctx: AuthContext,
    prompt_id: UUID,
    data: PromptVersionCreate,
) -> PromptVersion:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt or prompt.organization_id != ctx.organization.id:
        raise ValueError("Prompt not found")

    max_version = await db.scalar(
        select(func.max(PromptVersion.version_number)).where(PromptVersion.prompt_id == prompt_id)
    )
    next_version = (max_version or 0) + 1

    if data.parent_version_id:
        parent = await db.get(PromptVersion, data.parent_version_id)
        if not parent or parent.prompt_id != prompt_id:
            raise ValueError("Invalid parent version")

    version = PromptVersion(
        prompt_id=prompt.id,
        organization_id=ctx.organization.id,
        version_number=next_version,
        content=data.content,
        content_hash=content_hash(data.content),
        metadata_=data.metadata,
        parent_version_id=data.parent_version_id,
        created_by_id=ctx.user.id,
    )
    db.add(version)
    await db.flush()
    return version


async def promote_tag(
    db: AsyncSession,
    ctx: AuthContext,
    prompt_id: UUID,
    tag_name: str,
    version_id: UUID | None = None,
    version_number: int | None = None,
) -> PromptTag:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt or prompt.organization_id != ctx.organization.id:
        raise ValueError("Prompt not found")

    if not re.match(r"^[a-z0-9_-]+$", tag_name):
        raise ValueError("Invalid tag name")

    if version_id:
        version = await db.get(PromptVersion, version_id)
    elif version_number:
        result = await db.execute(
            select(PromptVersion).where(
                PromptVersion.prompt_id == prompt_id,
                PromptVersion.version_number == version_number,
            )
        )
        version = result.scalar_one_or_none()
    else:
        raise ValueError("version_id or version_number required")

    if not version or version.prompt_id != prompt_id:
        raise ValueError("Version not found")

    result = await db.execute(
        select(PromptTag).where(PromptTag.prompt_id == prompt_id, PromptTag.name == tag_name)
    )
    tag = result.scalar_one_or_none()
    if tag:
        tag.version_id = version.id
        tag.promoted_by_id = ctx.user.id
    else:
        tag = PromptTag(
            prompt_id=prompt.id,
            organization_id=ctx.organization.id,
            name=tag_name,
            version_id=version.id,
            promoted_by_id=ctx.user.id,
        )
        db.add(tag)
    await db.flush()
    return tag


async def resolve_prompt(
    db: AsyncSession, ctx: AuthContext, prompt_id: UUID, tag_name: str
) -> tuple[Prompt, PromptVersion, PromptTag]:
    prompt = await db.get(Prompt, prompt_id)
    if not prompt or prompt.organization_id != ctx.organization.id:
        raise ValueError("Prompt not found")

    result = await db.execute(
        select(PromptTag)
        .where(PromptTag.prompt_id == prompt_id, PromptTag.name == tag_name)
        .options(selectinload(PromptTag.version))
    )
    tag = result.scalar_one_or_none()
    if not tag:
        raise ValueError(f"Tag '{tag_name}' not found")

    return prompt, tag.version, tag
