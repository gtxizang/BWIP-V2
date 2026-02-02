"""
Models for the API application.

Provides models for device management and API tokens.
"""

import secrets

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class Device(TimeStampedModel):
    """
    Smart signage device for displaying water quality information.

    Each device belongs to a Local Authority and can display
    information for specific locations.

    Example:
        >>> device = Device.objects.create(
        ...     name="Beach Sign - Dollymount",
        ...     local_authority=dcc,
        ...     device_type=Device.DeviceType.DIGITAL_SIGN,
        ... )
    """

    class DeviceType(models.TextChoices):
        """Types of smart signage devices."""

        DIGITAL_SIGN = "DIGITAL_SIGN", _("Digital Sign")
        KIOSK = "KIOSK", _("Kiosk")
        DISPLAY_BOARD = "DISPLAY_BOARD", _("Display Board")
        OTHER = "OTHER", _("Other")

    name = models.CharField(
        _("name"),
        max_length=100,
    )
    local_authority = models.ForeignKey(
        "organisations.LocalAuthority",
        on_delete=models.CASCADE,
        related_name="devices",
        verbose_name=_("local authority"),
    )
    device_type = models.CharField(
        _("device type"),
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.DIGITAL_SIGN,
    )
    locations = models.ManyToManyField(
        "locations.Location",
        related_name="devices",
        verbose_name=_("locations"),
        blank=True,
        help_text=_("Locations this device can display"),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
    )
    last_seen = models.DateTimeField(
        _("last seen"),
        null=True,
        blank=True,
    )
    metadata = models.JSONField(
        _("metadata"),
        default=dict,
        blank=True,
        help_text=_("Additional device configuration"),
    )

    class Meta:
        verbose_name = _("device")
        verbose_name_plural = _("devices")
        ordering = ["name"]

    def __str__(self) -> str:
        """Return device name."""
        return self.name

    def update_last_seen(self) -> None:
        """Update the last seen timestamp."""
        self.last_seen = timezone.now()
        self.save(update_fields=["last_seen"])


class DeviceToken(TimeStampedModel):
    """
    Authentication token for a device.

    Used for API authentication from smart signage devices.

    Example:
        >>> token = DeviceToken.objects.create(device=device)
        >>> print(token.token)  # Use this in Authorization header
    """

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="tokens",
        verbose_name=_("device"),
    )
    token = models.CharField(
        _("token"),
        max_length=64,
        unique=True,
        editable=False,
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
    )
    last_used = models.DateTimeField(
        _("last used"),
        null=True,
        blank=True,
    )
    expires_at = models.DateTimeField(
        _("expires at"),
        null=True,
        blank=True,
        help_text=_("Leave blank for non-expiring token"),
    )

    class Meta:
        verbose_name = _("device token")
        verbose_name_plural = _("device tokens")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        """Return masked token representation."""
        return f"{self.device.name} - {self.token[:8]}..."

    def save(self, *args, **kwargs) -> None:
        """Generate token if not set."""
        if not self.token:
            self.token = self.generate_token()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_token() -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(48)

    def update_last_used(self) -> None:
        """Update the last used timestamp."""
        self.last_used = timezone.now()
        self.save(update_fields=["last_used"])

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at
