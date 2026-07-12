import enum

from app.models import Role


class Permission(str, enum.Enum):
    org_read = "org:read"
    org_manage_members = "org:manage_members"
    project_read = "project:read"
    project_write = "project:write"
    prompt_read = "prompt:read"
    prompt_write = "prompt:write"
    prompt_promote = "prompt:promote"
    provider_read = "provider:read"
    provider_write = "provider:write"
    routing_read = "routing:read"
    routing_write = "routing:write"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.owner: set(Permission),
    Role.admin: {
        Permission.org_read,
        Permission.org_manage_members,
        Permission.project_read,
        Permission.project_write,
        Permission.prompt_read,
        Permission.prompt_write,
        Permission.prompt_promote,
        Permission.provider_read,
        Permission.provider_write,
        Permission.routing_read,
        Permission.routing_write,
    },
    Role.editor: {
        Permission.org_read,
        Permission.project_read,
        Permission.project_write,
        Permission.prompt_read,
        Permission.prompt_write,
        Permission.prompt_promote,
        Permission.provider_read,
        Permission.routing_read,
    },
    Role.viewer: {
        Permission.org_read,
        Permission.project_read,
        Permission.prompt_read,
        Permission.provider_read,
        Permission.routing_read,
    },
}


def role_has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
