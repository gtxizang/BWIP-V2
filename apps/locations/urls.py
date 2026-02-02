"""URL patterns for the locations application."""

from django.urls import path

from . import views

app_name = "locations"

urlpatterns = [
    path("", views.LocationListView.as_view(), name="list"),
    path("<int:pk>/", views.LocationDetailView.as_view(), name="detail"),
    path("map-data/", views.LocationMapDataView.as_view(), name="map_data"),
]
