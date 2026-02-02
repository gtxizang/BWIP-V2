"""
Audit models for BWIP.

Provides immutable audit log entries for compliance tracking.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """
    Immutable audit log entry.

    Records all significant actions for compliance and auditing.
    Entries cannot be modified after creation.

    Example:
        >>> AuditLog.objects.create(
        ...     user=request.user,
        ...     action=AuditLog.Action.POSTER_GENERATED,
        ...     ip_address="192.168.1.1",
        ...     details={"template": "1A", "size": "A1"},
        ...     location=location,
        ...     poster=poster,
        ... )
    """

    class Action(models.TextChoices):
        """Audit log action types."""

        POSTER_GENERATED = "POSTER_GENERATED", _("Poster generated")
        SECTION_UPDATED = "SECTION_UPDATED", _("Section updated")
        USER_LOGIN = "USER_LOGIN", _("User login")
        USER_LOGOUT = "USER_LOGOUT", _("User logout")
        LOCATION_CREATED = "LOCATION_CREATED", _("Location created")
        LOCATION_MODIFIED = "LOCATION_MODIFIED", _("Location modified")
        ALERT_RECEIVED = "ALERT_RECEIVED", _("Alert received")
        DATA_SYNC = "DATA_SYNC", _("Data synchronised")
        USER_CREATED = "USER_CREATED", _("User created")
        USER_MODIFIED = "USER_MODIFIED", _("User modified")
        SETTINGS_CHANGED = "SETTINGS_CHANGED", _("Settings changed")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("user"),
    )
    action = models.CharField(
        _("action"),
        max_length=30,
        choices=Action.choices,
        db_index=True,
    )
    timestamp = models.DateTimeField(
        _("timestamp"),
        auto_now_add=True,
        db_index=True,
    )
    ip_address = models.GenericIPAddressField(
        _("IP address"),
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        _("user agent"),
        blank=True,
    )
    details = models.JSONField(
        _("details"),
        default=dict,
        help_text=_("Additional details about the action"),
    )

    # Optional relations for context
    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("location"),
    )
    poster = models.ForeignKey(
        "posters.Poster",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name=_("poster"),
    )

    class Meta:
        verbose_name = _("audit log")
        verbose_name_plural = _("audit logs")
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["user", "-timestamp"]),
            models.Index(fields=["action", "-timestamp"]),
        ]

    def __str__(self) -> str:
        """Return log entry description."""
        user_str = self.user.email if self.user else "System"
        return f"{self.action} by {user_str} at {self.timestamp}"

    def save(self, *args, **kwargs) -> None:
        """Prevent modification of existing entries."""
        if self.pk:
            raise ValueError("Audit logs cannot be modified after creation.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:
        """Prevent deletion of audit logs."""
        raise ValueError("Audit logs cannot be deleted.")
