"""Posters app configuration."""

from django.apps import AppConfig


class PostersConfig(AppConfig):
    """Configuration for the posters application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.posters"
    verbose_name = "Posters"
