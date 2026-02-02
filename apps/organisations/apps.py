"""Organisations app configuration."""

from django.apps import AppConfig


class OrganisationsConfig(AppConfig):
    """Configuration for the organisations application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.organisations"
    verbose_name = "Organisations"
