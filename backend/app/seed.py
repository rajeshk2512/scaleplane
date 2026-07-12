"""Seed default organization and optional demo data."""

import asyncio

from sqlalchemy import select

from app.core.database import async_session_factory
from app.models import Organization, OrganizationMember, Project, Prompt, PromptVersion, Role, User
from app.services import content_hash, ensure_default_organization


async def seed() -> None:
    async with async_session_factory() as db:
        org = await ensure_default_organization(db)

        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Seed skipped: users already exist")
            await db.commit()
            return

        from app.core.security import hash_password

        owner = User(
            email="owner@scaleplane.dev",
            password_hash=hash_password("password123"),
            full_name="ScalePlane Owner",
        )
        db.add(owner)
        await db.flush()

        db.add(
            OrganizationMember(
                user_id=owner.id,
                organization_id=org.id,
                role=Role.owner,
            )
        )

        project = Project(
            organization_id=org.id,
            name="Demo Project",
            slug="demo",
            description="Sample project for quick-start",
        )
        db.add(project)
        await db.flush()

        prompt = Prompt(
            project_id=project.id,
            organization_id=org.id,
            name="System Prompt",
            slug="system-prompt",
            description="Example system prompt",
        )
        db.add(prompt)
        await db.flush()

        content = "You are a helpful assistant for ScalePlane infrastructure."
        db.add(
            PromptVersion(
                prompt_id=prompt.id,
                organization_id=org.id,
                version_number=1,
                content=content,
                content_hash=content_hash(content),
                metadata_={"env": "demo"},
                created_by_id=owner.id,
            )
        )

        await db.commit()
        print("Seed complete: owner@scaleplane.dev / password123")


if __name__ == "__main__":
    asyncio.run(seed())
