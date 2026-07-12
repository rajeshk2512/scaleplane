from fastapi import APIRouter

from app.api.v1 import auth, organizations, projects, prompts, routing, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(organizations.router)
api_router.include_router(projects.router)
api_router.include_router(prompts.router)
api_router.include_router(routing.router)
