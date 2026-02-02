"""
Views for the locations application.

Handles listing and viewing bathing water locations.
"""

from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch, QuerySet
from django.http import JsonResponse
from django.views import View
from django.views.generic import DetailView, ListView

from apps.core.views import OrganisationPermissionMixin

from .models import Alert, Location, WaterQualityData


class LocationListView(LoginRequiredMixin, OrganisationPermissionMixin, ListView):
    """
    Display list of locations for the user's Local Authority.

    Shows all active bathing water locations with their current status.
    """

    model = Location
    template_name = "locations/location_list.html"
    context_object_name = "locations"
    paginate_by = 20

    def get_queryset(self) -> QuerySet[Location]:
        """Filter locations to user's organisation."""
        return (
            super()
            .get_queryset()
            .filter(
                local_authority=self.get_organisation(),
                is_active=True,
            )
            .select_related("local_authority")
            .prefetch_related(
                Prefetch(
                    "water_quality_data",
                    queryset=WaterQualityData.objects.filter(is_current=True),
                ),
                Prefetch(
                    "alerts",
                    queryset=Alert.objects.filter(is_active=True),
                ),
            )
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add filter options and counts to context."""
        context = super().get_context_data(**kwargs)
        context["classification_choices"] = Location.Classification.choices
        context["total_count"] = self.get_queryset().count()
        return context


class LocationDetailView(LoginRequiredMixin, OrganisationPermissionMixin, DetailView):
    """
    Display details of a specific location.

    Shows location details, current water quality, and active alerts.
    """

    model = Location
    template_name = "locations/location_detail.html"
    context_object_name = "location"

    def get_queryset(self) -> QuerySet[Location]:
        """Filter to user's organisation."""
        return (
            super()
            .get_queryset()
            .filter(local_authority=self.get_organisation())
            .select_related("local_authority")
        )

    def get_object(self, queryset=None) -> Location:
        """Get the location and verify access."""
        obj = super().get_object(queryset)
        self.check_object_organisation(obj)
        return obj

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add water quality and alert data to context."""
        context = super().get_context_data(**kwargs)
        location = self.object

        # Get current water quality
        context["current_quality"] = location.get_current_water_quality()

        # Get recent water quality history
        context["quality_history"] = location.water_quality_data.order_by(
            "-sample_date"
        )[:10]

        # Get active alerts
        context["active_alerts"] = location.get_active_alerts()

        # Get facilities
        context["facilities"] = location.get_facilities()

        return context


class LocationMapDataView(LoginRequiredMixin, OrganisationPermissionMixin, View):
    """
    API endpoint returning location data for map display.

    Returns GeoJSON-like data for rendering on a Leaflet map.
    """

    def get(self, request, *args, **kwargs) -> JsonResponse:
        """Return location data as JSON."""
        locations = Location.objects.filter(
            local_authority=self.get_organisation(),
            is_active=True,
        ).select_related("local_authority")

        data = []
        for loc in locations:
            current_quality = loc.get_current_water_quality()
            has_alert = loc.has_active_alert()

            data.append(
                {
                    "id": loc.id,
                    "name": loc.name_en,
                    "name_ga": loc.name_ga,
                    "lat": float(loc.latitude),
                    "lng": float(loc.longitude),
                    "classification": loc.classification,
                    "has_alert": has_alert,
                    "quality_status": (
                        current_quality.quality_status if current_quality else None
                    ),
                    "beaches_ie_id": loc.beaches_ie_id,
                }
            )

        return JsonResponse({"locations": data})
