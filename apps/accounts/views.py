"""
Views for the accounts application.

Handles profile management. Authentication is handled by django-allauth.
"""

from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView

from .forms import UserProfileForm
from .models import UserProfile


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View for displaying user profile.

    Shows the current user's profile information and organisation.
    """

    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add profile data to context."""
        context = super().get_context_data(**kwargs)
        context["profile"] = getattr(self.request.user, "userprofile", None)
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating user profile.

    Allows users to edit their profile information.
    """

    model = UserProfile
    form_class = UserProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None) -> UserProfile:
        """Get the current user's profile."""
        return self.request.user.userprofile

    def form_valid(self, form) -> HttpResponse:
        """Show success message on valid form submission."""
        messages.success(self.request, _("Profile updated successfully."))
        return super().form_valid(form)
