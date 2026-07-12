from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import ProviderType, Role


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    full_name: str | None
    created_at: datetime


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    name: str
    is_default: bool
    created_at: datetime


class MemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    email: str
    full_name: str | None
    role: Role
    created_at: datetime


class MemberCreate(BaseModel):
    email: EmailStr
    role: Role = Role.viewer


class MemberUpdate(BaseModel):
    role: Role


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    slug: str
    description: str | None
    created_at: datetime


class PromptCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: str | None = None
    content: str = Field(min_length=1)
    metadata: dict | None = None


class PromptResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    organization_id: UUID
    name: str
    slug: str
    description: str | None
    created_at: datetime
    latest_version_number: int | None = None
    production_tag_version: int | None = None


class PromptVersionCreate(BaseModel):
    content: str = Field(min_length=1)
    metadata: dict | None = None
    parent_version_id: UUID | None = None


class PromptVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    prompt_id: UUID
    version_number: int
    content: str
    content_hash: str
    metadata: dict | None = Field(default=None, validation_alias="metadata_")
    parent_version_id: UUID | None
    created_by_id: UUID | None
    created_at: datetime


class PromptTagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    prompt_id: UUID
    name: str
    version_id: UUID
    version_number: int
    promoted_at: datetime


class PromptResolveResponse(BaseModel):
    prompt_id: UUID
    prompt_slug: str
    tag: str
    version_id: UUID
    version_number: int
    content: str
    content_hash: str
    metadata: dict | None = None


class ProviderCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    provider_type: ProviderType
    config: dict = Field(default_factory=dict)
    is_active: bool = True


class ProviderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    provider_type: ProviderType
    config: dict
    is_active: bool
    created_at: datetime


class RoutingPolicyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    rules: dict = Field(default_factory=dict)
    is_active: bool = True


class RoutingPolicyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    name: str
    rules: dict
    is_active: bool
    created_at: datetime


class CompletionRequest(BaseModel):
    prompt_id: UUID | None = None
    prompt_slug: str | None = None
    tag: str = "production"
    messages: list[dict] = Field(default_factory=list)
    model: str | None = None


class CompletionNotImplementedResponse(BaseModel):
    detail: str
    message: str
    future_capabilities: list[str]
