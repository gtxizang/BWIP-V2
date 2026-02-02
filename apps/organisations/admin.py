"""Admin configuration for the organisations application."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import LocalAuthority


@admin.register(LocalAuthority)
class LocalAuthorityAdmin(admin.ModelAdmin):
    """Admin configuration for LocalAuthority model."""

    list_display = (
        "name",
        "code",
        "contact_email",
        "get_users_count",
        "get_locations_count",
    )
    list_filter = ("is_active",)
    search_fields = ("name", "code", "contact_email")
    fieldsets = (
        (None, {"fields": ("name", "code", "is_active")}),
        (
            _("Contact Information"),
            {
                "fields": (
                    "contact_email",
                    "email_domain",
                    "phone",
                    "address",
                    "website",
                )
            },
        ),
        (
            _("Branding"),
            {"fields": ("logo", "primary_colour", "secondary_colour")},
        ),
    )

    def get_users_count(self, obj: LocalAuthority) -> int:
        """Get count of users."""
        return obj.get_active_users_count()

    get_users_count.short_description = _("Users")

    def get_locations_count(self, obj: LocalAuthority) -> int:
        """Get count of locations."""
        return obj.get_locations_count()

    get_locations_count.short_description = _("Locations")
