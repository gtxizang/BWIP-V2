"""
Middleware for the audit application.

Provides request tracking and context for audit logging.
"""

import threading
from typing import Callable

from django.http import HttpRequest, HttpResponse

# Thread-local storage for request context
_request_local = threading.local()


def get_current_request() -> HttpRequest | None:
    """Get the current request from thread-local storage."""
    return getattr(_request_local, "request", None)


def get_current_user():
    """Get the current user from thread-local storage."""
    request = get_current_request()
    if request and hasattr(request, "user") and request.user.is_authenticated:
        return request.user
    return None


class AuditMiddleware:
    """
    Middleware for storing request context for audit logging.

    Stores the current request in thread-local storage so it can
    be accessed from signals and other contexts.

    Usage:
        Add 'apps.audit.middleware.AuditMiddleware' to MIDDLEWARE setting.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request and store in thread-local storage."""
        _request_local.request = request
        try:
            response = self.get_response(request)
        finally:
            # Clean up thread-local storage
            if hasattr(_request_local, "request"):
                del _request_local.request
        return response
