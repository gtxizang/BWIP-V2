"""
Exceptions for the beaches.ie API service.

Custom exceptions for handling API-specific errors.
"""

from apps.core.exceptions import ExternalServiceError


class BeachesAPIError(ExternalServiceError):
    """Base exception for beaches.ie API errors."""

    default_message = "beaches.ie API error occurred."


class BeachesAPITimeout(BeachesAPIError):
    """Raised when API request times out."""

    default_message = "beaches.ie API request timed out."


class BeachesAPINotFound(BeachesAPIError):
    """Raised when requested resource not found."""

    default_message = "Requested resource not found on beaches.ie."


class BeachesAPIRateLimited(BeachesAPIError):
    """Raised when API rate limit is exceeded."""

    default_message = "beaches.ie API rate limit exceeded."


class BeachesAPIInvalidResponse(BeachesAPIError):
    """Raised when API returns invalid/malformed response."""

    default_message = "beaches.ie API returned invalid response."
