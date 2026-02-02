"""Admin configuration for the locations application."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Alert, Location, WaterQualityData


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin configuration for Location model."""

    list_display = (
        "name_en",
        "local_authority",
        "classification",
        "beaches_ie_id",
        "is_active",
        "has_active_alert_display",
    )
    list_filter = ("classification", "local_authority", "is_active")
    search_fields = ("name_en", "name_ga", "beaches_ie_id")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("local_authority",)
    fieldsets = (
        (None, {"fields": ("name_en", "name_ga", "local_authority", "beaches_ie_id")}),
        (
            _("Classification"),
            {"fields": ("classification", "is_active")},
        ),
        (
            _("Location"),
            {"fields": ("latitude", "longitude")},
        ),
        (
            _("Description"),
            {"fields": ("description_en", "description_ga")},
        ),
        (
            _("Facilities"),
            {
                "fields": (
                    "has_toilets",
                    "has_parking",
                    "has_lifeguard",
                    "has_disability_access",
                    "has_blue_flag",
                    "dogs_allowed",
                )
            },
        ),
        (
            _("Timestamps"),
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def has_active_alert_display(self, obj: Location) -> bool:
        """Display whether location has active alert."""
        return obj.has_active_alert()

    has_active_alert_display.boolean = True
    has_active_alert_display.short_description = _("Active Alert")


@admin.register(WaterQualityData)
class WaterQualityDataAdmin(admin.ModelAdmin):
    """Admin configuration for WaterQualityData model."""

    list_display = (
        "location",
        "sample_date",
        "quality_status",
        "ecoli_value",
        "enterococci_value",
        "is_current",
    )
    list_filter = ("quality_status", "is_current", "sample_date")
    search_fields = ("location__name_en",)
    raw_id_fields = ("location",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "sample_date"


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Admin configuration for Alert model."""

    list_display = (
        "location",
        "alert_type",
        "title_en",
        "start_date",
        "end_date",
        "is_active",
        "is_season_long",
    )
    list_filter = ("alert_type", "is_active", "is_season_long", "start_date")
    search_fields = ("location__name_en", "title_en", "title_ga")
    raw_id_fields = ("location",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "start_date"
