"""URL patterns for the API application."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
router.register(r"locations", views.LocationViewSet, basename="location")

urlpatterns = [
    path("", include(router.urls)),
]
