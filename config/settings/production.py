"""
Production settings for BWIP.

These settings are for production deployment.
Ensure all security settings are properly configured.
"""

from .base import *  # noqa: F401, F403

# =============================================================================
# Debug Settings
# =============================================================================

DEBUG = False

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())  # noqa: F405

# =============================================================================
# Security Settings
# =============================================================================

# HTTPS settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookie settings
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# Content type options
SECURE_CONTENT_TYPE_NOSNIFF = True

# XSS filter
SECURE_BROWSER_XSS_FILTER = True

# X-Frame-Options
X_FRAME_OPTIONS = "DENY"

# =============================================================================
# Static and Media Files - Production
# =============================================================================

# Configure for your production storage (S3, etc.)
# STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# =============================================================================
# beaches.ie API - Production
# =============================================================================

# Use real API in production
BEACHES_API["USE_MOCK_DATA"] = False  # noqa: F405

# =============================================================================
# Logging - Production
# =============================================================================

LOGGING["handlers"]["file"]["filename"] = "/var/log/bwip/bwip.log"  # noqa: F405
LOGGING["root"]["handlers"] = ["file"]  # noqa: F405
LOGGING["loggers"]["apps"]["handlers"] = ["file"]  # noqa: F405
LOGGING["loggers"]["services"]["handlers"] = ["file"]  # noqa: F405
