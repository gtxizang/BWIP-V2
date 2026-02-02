"""Locations app configuration."""

from django.apps import AppConfig


class LocationsConfig(AppConfig):
    """Configuration for the locations application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.locations"
    verbose_name = "Locations"
