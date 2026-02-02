"""Admin configuration for the API application."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Device, DeviceToken


class DeviceTokenInline(admin.TabularInline):
    """Inline admin for device tokens."""

    model = DeviceToken
    extra = 0
    readonly_fields = ("token", "last_used", "created_at")
    fields = ("token", "is_active", "expires_at", "last_used", "created_at")


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Admin configuration for Device model."""

    list_display = (
        "name",
        "local_authority",
        "device_type",
        "is_active",
        "last_seen",
    )
    list_filter = ("device_type", "is_active", "local_authority")
    search_fields = ("name", "local_authority__name")
    raw_id_fields = ("local_authority",)
    filter_horizontal = ("locations",)
    inlines = [DeviceTokenInline]
    readonly_fields = ("last_seen", "created_at", "updated_at")


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    """Admin configuration for DeviceToken model."""

    list_display = (
        "device",
        "masked_token",
        "is_active",
        "last_used",
        "expires_at",
    )
    list_filter = ("is_active",)
    search_fields = ("device__name",)
    raw_id_fields = ("device",)
    readonly_fields = ("token", "last_used", "created_at", "updated_at")

    def masked_token(self, obj: DeviceToken) -> str:
        """Display masked token."""
        return f"{obj.token[:8]}..."

    masked_token.short_description = _("Token")
