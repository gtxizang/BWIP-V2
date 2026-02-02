"""
Test settings for BWIP.

These settings are used when running pytest.
"""

from .base import *  # noqa: F401, F403

# =============================================================================
# Debug Settings
# =============================================================================

DEBUG = False

# =============================================================================
# Database - Use SQLite for Fast Tests
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# =============================================================================
# Password Hashing - Faster for Tests
# =============================================================================

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# =============================================================================
# Email - Test Backend
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# =============================================================================
# beaches.ie API - Always Use Mock Data in Tests
# =============================================================================

BEACHES_API["USE_MOCK_DATA"] = True  # noqa: F405
BEACHES_API["CACHE_TIMEOUT"] = 0  # noqa: F405

# =============================================================================
# Media - Use Temporary Directory
# =============================================================================

import tempfile

MEDIA_ROOT = tempfile.mkdtemp()

# =============================================================================
# Logging - Minimal for Tests
# =============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "DEBUG",
    },
}
