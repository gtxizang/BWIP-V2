"""
Views for the API application.

Provides REST API endpoints for smart signage devices.
"""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.locations.models import Location

from .authentication import DeviceTokenAuthentication
from .serializers import LocationListSerializer, LocationSerializer


class IsDeviceAuthenticated(permissions.BasePermission):
    """
    Permission class for device authentication.

    Allows access if request has valid device token authentication.
    """

    def has_permission(self, request, view) -> bool:
        """Check if device is authenticated."""
        return (
            request.auth is not None
            and hasattr(request.auth, "device")
            and request.auth.device.is_active
        )


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for locations.

    Provides read-only access to locations for smart signage devices.

    Endpoints:
        GET /api/v1/locations/ - List all accessible locations
        GET /api/v1/locations/{id}/ - Get location details
        GET /api/v1/locations/{id}/water_quality/ - Get current water quality
    """

    authentication_classes = [DeviceTokenAuthentication]
    permission_classes = [IsDeviceAuthenticated]
    serializer_class = LocationSerializer

    def get_queryset(self):
        """
        Filter locations to those accessible by the device.

        Returns locations that:
        1. Belong to the device's local authority
        2. Are assigned to the device (if device has specific locations)
        3. Are active
        """
        device = self.request.auth.device

        queryset = Location.objects.filter(
            local_authority=device.local_authority,
            is_active=True,
        ).select_related("local_authority")

        # If device has specific locations assigned, filter to those
        device_locations = device.locations.all()
        if device_locations.exists():
            queryset = queryset.filter(pk__in=device_locations)

        return queryset

    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == "list":
            return LocationListSerializer
        return LocationSerializer

    @action(detail=True, methods=["get"])
    def water_quality(self, request, pk=None):
        """
        Get current water quality for a location.

        Returns the most recent water quality measurement.
        """
        location = self.get_object()
        quality = location.get_current_water_quality()

        if quality is None:
            return Response(
                {"detail": "No water quality data available."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from .serializers import WaterQualityDataSerializer

        serializer = WaterQualityDataSerializer(quality)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def alerts(self, request, pk=None):
        """
        Get active alerts for a location.

        Returns all currently active alerts.
        """
        location = self.get_object()
        alerts = location.get_active_alerts()

        from .serializers import AlertSerializer

        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)
