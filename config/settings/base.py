"""
Base Django settings for BWIP.

Contains settings shared across all environments.
Environment-specific settings should go in development.py, production.py, or test.py.
"""

import os
from pathlib import Path

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# Core Django Settings
# =============================================================================

SECRET_KEY = config("SECRET_KEY", default="django-insecure-change-this-in-production")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

# =============================================================================
# Application Definition
# =============================================================================

DJANGO_APPS = [
    "jazzmin",  # Must be before django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Required by allauth
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_extensions",
    # Authentication
    "allauth",
    "allauth.account",
    "allauth.mfa",
]

# Site ID for django.contrib.sites (required by allauth)
SITE_ID = 1

# =============================================================================
# Jazzmin Admin Theme
# =============================================================================

JAZZMIN_SETTINGS = {
    "site_title": "BWIP Admin",
    "site_header": "BWIP",
    "site_brand": "BWIP v2",
    "site_logo": None,
    "welcome_sign": "Bathing Water Information Portal",
    "copyright": "BWIP",
    "search_model": ["locations.Location", "auth.User"],
    "topmenu_links": [
        {"name": "Dashboard", "url": "/", "new_window": False},
        {"name": "beaches.ie", "url": "https://www.beaches.ie", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "locations.Location": "fas fa-map-marker-alt",
        "locations.WaterQualityData": "fas fa-tint",
        "locations.Alert": "fas fa-exclamation-triangle",
        "organisations.LocalAuthority": "fas fa-building",
        "posters.Poster": "fas fa-file-pdf",
        "posters.PosterTemplate": "fas fa-palette",
        "audit.AuditLog": "fas fa-history",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "use_google_fonts_cdn": True,
    "changeform_format": "horizontal_tabs",
}

LOCAL_APPS = [
    "apps.core",
    "apps.accounts",
    "apps.organisations",
    "apps.locations",
    "apps.posters",
    "apps.api",
    "apps.audit",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# =============================================================================
# Middleware
# =============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.audit.middleware.AuditMiddleware",
]

ROOT_URLCONF = "config.urls"

# =============================================================================
# Templates
# =============================================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# =============================================================================
# Database
# =============================================================================

import dj_database_url

DATABASE_URL = config(
    "DATABASE_URL",
    default="postgresql://postgres:postgres@localhost:5432/bwip_v2",
)

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# =============================================================================
# Authentication
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "posters:dashboard"
LOGOUT_REDIRECT_URL = "account_login"

# =============================================================================
# Django-Allauth Configuration
# =============================================================================

# Login with email only (no username)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGIN_BY_CODE_ENABLED = True

# =============================================================================
# MFA Configuration
# =============================================================================

MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_TOTP_ISSUER = "BWIP"
MFA_PASSKEY_LOGIN_ENABLED = True
# Require MFA for all users in production (can be overridden per-environment)
MFA_ENFORCEMENT = config("MFA_ENFORCEMENT", default="optional")  # "required", "optional", or "staff_required"

# =============================================================================
# Internationalisation
# =============================================================================

LANGUAGE_CODE = "en-gb"

TIME_ZONE = "Europe/Dublin"

USE_I18N = True

USE_TZ = True

# =============================================================================
# Static Files
# =============================================================================

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# =============================================================================
# Media Files
# =============================================================================

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# =============================================================================
# Default Primary Key Field Type
# =============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# =============================================================================
# Django REST Framework
# =============================================================================

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "apps.api.authentication.DeviceTokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

# =============================================================================
# beaches.ie API Configuration
# =============================================================================

BEACHES_API = {
    "BASE_URL": config(
        "BEACHES_API_BASE_URL",
        default="https://data.epa.ie/bw/api/v1",
    ),
    "TIMEOUT": config("BEACHES_API_TIMEOUT", default=10, cast=int),
    "CACHE_TIMEOUT": config("BEACHES_API_CACHE_TIMEOUT", default=3600, cast=int),
    "USE_MOCK_DATA": config("BEACHES_API_USE_MOCK", default=False, cast=bool),
}

# =============================================================================
# PDF Generation Settings
# =============================================================================

PDF_GENERATION = {
    "DPI": 300,
    "SIZES": {
        "A1": (594, 841),
        "A3": (297, 420),
        "A4": (210, 297),
        "A5": (148, 210),
    },
    "DEFAULT_SIZE": "A1",
    "DEFAULT_ORIENTATION": "PORTRAIT",
}

# =============================================================================
# Logging Configuration
# =============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "bwip.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": config("DJANGO_LOG_LEVEL", default="INFO"),
            "propagate": False,
        },
        "apps": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "services": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# Create logs directory if it doesn't exist
(BASE_DIR / "logs").mkdir(exist_ok=True)
