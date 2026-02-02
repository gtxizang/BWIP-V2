"""
Views for the accounts application.

Handles user authentication, profile management, and account-related pages.
"""

from typing import Any

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView

from apps.audit.models import AuditLog

from .forms import EmailAuthenticationForm, UserProfileForm
from .models import UserProfile


class CustomLoginView(LoginView):
    """
    Custom login view using email authentication.

    Renders the login page and handles authentication.
    """

    template_name = "accounts/login.html"
    form_class = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self) -> str:
        """Return the URL to redirect to after login."""
        return self.get_redirect_url() or reverse_lazy("posters:dashboard")

    def form_valid(self, form) -> HttpResponse:
        """Log successful login and redirect."""
        response = super().form_valid(form)

        # Log the login
        AuditLog.objects.create(
            user=self.request.user,
            action=AuditLog.Action.USER_LOGIN,
            ip_address=self.get_client_ip(),
            details={"email": self.request.user.email},
        )

        messages.success(self.request, _("Welcome back!"))
        return response

    def get_client_ip(self) -> str | None:
        """Get the client's IP address from the request."""
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return self.request.META.get("REMOTE_ADDR")


class CustomLogoutView(LogoutView):
    """
    Custom logout view with audit logging.

    Logs out the user and redirects to login page.
    """

    next_page = reverse_lazy("accounts:login")

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Log the logout before processing."""
        if request.user.is_authenticated:
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Action.USER_LOGOUT,
                ip_address=self.get_client_ip(request),
                details={"email": request.user.email},
            )
        return super().dispatch(request, *args, **kwargs)

    def get_client_ip(self, request: HttpRequest) -> str | None:
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


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
