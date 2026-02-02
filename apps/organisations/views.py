"""
Views for the organisations application.

Provides views for Local Authority management.
"""

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from apps.core.views import OrganisationPermissionMixin, StaffRequiredMixin

from .models import LocalAuthority


class LocalAuthorityListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    List all Local Authorities.

    Only accessible to staff users for administration purposes.
    """

    model = LocalAuthority
    template_name = "organisations/localauthority_list.html"
    context_object_name = "local_authorities"
    paginate_by = 20

    def get_queryset(self):
        """Get all Local Authorities."""
        return super().get_queryset().order_by("name")


class LocalAuthorityDetailView(
    LoginRequiredMixin, OrganisationPermissionMixin, DetailView
):
    """
    View details of a Local Authority.

    Users can only view their own organisation's details.
    """

    model = LocalAuthority
    template_name = "organisations/localauthority_detail.html"
    context_object_name = "local_authority"

    def get_object(self, queryset=None) -> LocalAuthority:
        """Return the user's own Local Authority."""
        return self.get_organisation()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        la = self.object
        context["users_count"] = la.get_active_users_count()
        context["locations_count"] = la.get_locations_count()
        return context
