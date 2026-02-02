"""
Development settings for BWIP.

These settings are only for local development.
DO NOT use these settings in production.
"""

from .base import *  # noqa: F401, F403

# =============================================================================
# Debug Settings
# =============================================================================

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# =============================================================================
# Development Apps
# =============================================================================

try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

# =============================================================================
# Database - Development
# =============================================================================

# Use the default from base.py or override here
# DATABASES["default"] = {
#     "ENGINE": "django.db.backends.postgresql",
#     "NAME": "bwip_v2",
#     "USER": "postgres",
#     "PASSWORD": "postgres",
#     "HOST": "localhost",
#     "PORT": "5432",
# }

# =============================================================================
# Email - Development (Console Backend)
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# beaches.ie API - Development
# =============================================================================

# Enable mock data for development if needed
BEACHES_API["USE_MOCK_DATA"] = config("BEACHES_API_USE_MOCK", default=True, cast=bool)  # noqa: F405

# =============================================================================
# Security - Relaxed for Development
# =============================================================================

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# =============================================================================
# Logging - More Verbose for Development
# =============================================================================

LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["services"]["level"] = "DEBUG"  # noqa: F405
