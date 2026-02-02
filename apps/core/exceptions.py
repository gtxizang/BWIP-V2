"""
Core exceptions for BWIP.

Provides base exception classes that other applications can inherit from.
"""


class BWIPException(Exception):
    """
    Base exception for all BWIP-specific exceptions.

    All custom exceptions in the project should inherit from this class.
    """

    default_message = "An error occurred in BWIP."

    def __init__(self, message: str | None = None, *args, **kwargs):
        """
        Initialize the exception.

        Args:
            message: Optional custom error message. Uses default_message if not provided.
        """
        self.message = message or self.default_message
        super().__init__(self.message, *args, **kwargs)


class ValidationError(BWIPException):
    """Raised when data validation fails."""

    default_message = "Validation failed."


class ConfigurationError(BWIPException):
    """Raised when there's a configuration error."""

    default_message = "Configuration error."


class ExternalServiceError(BWIPException):
    """Raised when an external service fails."""

    default_message = "External service error."


class PermissionError(BWIPException):
    """Raised when permission is denied."""

    default_message = "Permission denied."


class NotFoundError(BWIPException):
    """Raised when a resource is not found."""

    default_message = "Resource not found."
