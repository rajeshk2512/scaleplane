"""Resource modules — add new domains here without modifying transport/auth."""

from scaleplane.resources.prompts import PromptsResource
from scaleplane.resources.routing import RoutingResource

__all__ = ["PromptsResource", "RoutingResource"]
