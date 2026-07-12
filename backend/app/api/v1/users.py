from typing import Annotated

from fastapi import APIRouter, Depends

from app.rbac.deps import get_current_user
from app.models import User
from app.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user
