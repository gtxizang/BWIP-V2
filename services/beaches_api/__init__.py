"""
beaches.ie API integration service.

Provides client for fetching bathing water data from the EPA beaches.ie API.
"""

from .client import BeachesAPIClient, BeachesAPIConfig
from .exceptions import BeachesAPIError, BeachesAPINotFound, BeachesAPITimeout

__all__ = [
    "BeachesAPIClient",
    "BeachesAPIConfig",
    "BeachesAPIError",
    "BeachesAPINotFound",
    "BeachesAPITimeout",
]
