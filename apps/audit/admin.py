"""Admin configuration for the audit application."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin configuration for AuditLog model."""

    list_display = (
        "timestamp",
        "action",
        "user",
        "ip_address",
        "location",
        "poster",
    )
    list_filter = ("action", "timestamp")
    search_fields = ("user__email", "ip_address", "details")
    raw_id_fields = ("user", "location", "poster")
    date_hierarchy = "timestamp"
    readonly_fields = (
        "user",
        "action",
        "timestamp",
        "ip_address",
        "user_agent",
        "details",
        "location",
        "poster",
    )
    ordering = ("-timestamp",)

    def has_add_permission(self, request) -> bool:
        """Prevent manual creation of audit logs."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Prevent modification of audit logs."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Prevent deletion of audit logs."""
        return False
