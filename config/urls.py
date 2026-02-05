"""
URL configuration for BWIP project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.core.views import HealthCheckView

urlpatterns = [
    # Health check (for Docker/K8s probes)
    path("health/", HealthCheckView.as_view(), name="health_check"),
    # Admin
    path("admin/", admin.site.urls),
    # Authentication (django-allauth with MFA)
    path("accounts/", include("allauth.urls")),
    # Profile management
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),
    # Main apps
    path("", include("apps.posters.urls", namespace="posters")),
    path("locations/", include("apps.locations.urls", namespace="locations")),
    path("organisations/", include("apps.organisations.urls", namespace="organisations")),
    # API
    path("api/v1/", include("apps.api.urls", namespace="api")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

    # Debug toolbar
    try:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
