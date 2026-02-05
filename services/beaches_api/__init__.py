"""
beaches.ie API integration service.

Provides client for fetching bathing water data from the EPA beaches.ie API.
"""

from .client import BeachesAPIClient, BeachesAPIConfig
from .exceptions import (
    BeachesAPIError,
    BeachesAPIInvalidResponse,
    BeachesAPINotFound,
    BeachesAPITimeout,
)

__all__ = [
    "BeachesAPIClient",
    "BeachesAPIConfig",
    "BeachesAPIError",
    "BeachesAPIInvalidResponse",
    "BeachesAPINotFound",
    "BeachesAPITimeout",
]
