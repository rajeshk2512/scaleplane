from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import get_settings
from app.core.database import async_session_factory
from app.services import ensure_default_organization


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_session_factory() as session:
        await ensure_default_organization(session)
        await session.commit()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ScalePlane API",
        description="Enterprise infrastructure for agentic systems — prompt versioning and routing control plane",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app


app = create_app()
