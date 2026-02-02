"""
Core view mixins for BWIP.

Provides reusable view mixins for authentication, organisation permissions,
and other common view functionality.
"""

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.views import View
from django.views.generic import TemplateView


class HealthCheckView(View):
    """
    Health check endpoint for container orchestration.

    Returns JSON with status of critical services.
    Used by Docker, Kubernetes, load balancers for liveness/readiness probes.

    Example response:
        {"status": "healthy", "database": "ok", "version": "2.0.0"}
    """

    def get(self, request: HttpRequest) -> JsonResponse:
        """Return health status."""
        health = {
            "status": "healthy",
            "version": "2.0.0",
        }

        # Check database connectivity
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            health["database"] = "ok"
        except Exception as e:
            health["status"] = "unhealthy"
            health["database"] = f"error: {str(e)}"

        status_code = 200 if health["status"] == "healthy" else 503
        return JsonResponse(health, status=status_code)


class OrganisationPermissionMixin(UserPassesTestMixin):
    """
    Mixin ensuring user can only access their organisation's data.

    Requires the user to have a UserProfile with an associated LocalAuthority.
    Views using this mixin can access the user's organisation via `get_organisation()`.

    Example:
        >>> class MyView(LoginRequiredMixin, OrganisationPermissionMixin, ListView):
        ...     model = Location
        ...
        ...     def get_queryset(self):
        ...         return super().get_queryset().filter(
        ...             local_authority=self.get_organisation()
        ...         )
    """

    def test_func(self) -> bool:
        """Check user has a valid organisation."""
        user = self.request.user
        if not user.is_authenticated:
            return False
        if not hasattr(user, "userprofile"):
            return False
        return user.userprofile.local_authority is not None

    def get_organisation(self):
        """
        Get the user's organisation (Local Authority).

        Returns:
            LocalAuthority instance or None if user has no organisation.
        """
        if hasattr(self.request.user, "userprofile"):
            return self.request.user.userprofile.local_authority
        return None

    def check_object_organisation(self, obj: Any) -> None:
        """
        Verify user can access a specific object based on its local_authority.

        Args:
            obj: Any model instance with a local_authority or local_authority_id attribute.

        Raises:
            PermissionDenied: If user doesn't have access to the object's organisation.
        """
        user_org = self.get_organisation()
        if user_org is None:
            raise PermissionDenied("You don't belong to any organisation.")

        # Handle both direct FK and FK ID
        obj_org_id = getattr(obj, "local_authority_id", None)
        if obj_org_id is None:
            obj_org = getattr(obj, "local_authority", None)
            obj_org_id = obj_org.id if obj_org else None

        if obj_org_id != user_org.id:
            raise PermissionDenied("You don't have access to this resource.")


class StaffRequiredMixin(UserPassesTestMixin):
    """
    Mixin requiring user to be staff member.

    Use for views that should only be accessible to staff users.
    """

    def test_func(self) -> bool:
        """Check if user is staff."""
        return self.request.user.is_authenticated and self.request.user.is_staff


class SuperuserRequiredMixin(UserPassesTestMixin):
    """
    Mixin requiring user to be superuser.

    Use for views that should only be accessible to superusers.
    """

    def test_func(self) -> bool:
        """Check if user is superuser."""
        return self.request.user.is_authenticated and self.request.user.is_superuser


class AjaxResponseMixin:
    """
    Mixin for views that need to respond differently to AJAX requests.

    Provides utilities for detecting AJAX requests and returning appropriate responses.
    """

    def is_ajax(self) -> bool:
        """Check if the request is an AJAX request."""
        return self.request.headers.get("X-Requested-With") == "XMLHttpRequest"


class PageTitleMixin:
    """
    Mixin for adding page title to template context.

    Set `page_title` attribute on the view to include it in the context.
    """

    page_title: str = ""

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add page_title to the context."""
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title or self.get_page_title()
        return context

    def get_page_title(self) -> str:
        """Override to dynamically generate page title."""
        return self.page_title


class DashboardView(LoginRequiredMixin, OrganisationPermissionMixin, TemplateView):
    """
    Base dashboard view requiring login and organisation membership.

    Inherit from this for organisation-specific dashboard views.
    """

    template_name = "dashboard.html"
