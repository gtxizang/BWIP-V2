"""
User profile models for BWIP.

Extends Django's built-in User model with additional profile information
and Local Authority association for multi-tenancy.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class UserProfile(TimeStampedModel):
    """
    Extended user profile with Local Authority association.

    Links Django User to a Local Authority and provides role-based access control.
    Each user belongs to exactly one Local Authority.

    Example:
        >>> user = User.objects.get(email="user@example.com")
        >>> profile = user.userprofile
        >>> profile.local_authority.name
        'Dublin City Council'
    """

    class Role(models.TextChoices):
        """User roles within their Local Authority."""

        ADMIN = "ADMIN", _("Administrator")
        LA_ADMIN = "LA_ADMIN", _("Local Authority Admin")
        OFFICER = "OFFICER", _("Officer")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="userprofile",
        verbose_name=_("user"),
    )
    local_authority = models.ForeignKey(
        "organisations.LocalAuthority",
        on_delete=models.PROTECT,
        related_name="user_profiles",
        verbose_name=_("local authority"),
        null=True,
        blank=True,
        help_text=_("The Local Authority this user belongs to"),
    )
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=Role.choices,
        default=Role.OFFICER,
        help_text=_("User's role within their Local Authority"),
    )
    phone = models.CharField(
        _("phone number"),
        max_length=20,
        blank=True,
        help_text=_("Contact phone number"),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Whether this user profile is active"),
    )

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")
        ordering = ["user__email"]

    def __str__(self) -> str:
        """Return the user's email as string representation."""
        return self.user.email

    @property
    def full_name(self) -> str:
        """Get the user's full name."""
        return self.user.get_full_name() or self.user.email

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == self.Role.ADMIN

    @property
    def is_la_admin(self) -> bool:
        """Check if user has LA admin role or higher."""
        return self.role in (self.Role.ADMIN, self.Role.LA_ADMIN)

    def can_manage_users(self) -> bool:
        """Check if user can manage other users in their organisation."""
        return self.is_la_admin

    def can_access_location(self, location) -> bool:
        """
        Check if user can access a specific location.

        Args:
            location: Location instance to check access for.

        Returns:
            True if the location belongs to the user's Local Authority.
        """
        if self.local_authority is None:
            return False
        return location.local_authority_id == self.local_authority_id
