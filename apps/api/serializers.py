"""
Serializers for the API application.

Provides serializers for REST API endpoints.
"""

from rest_framework import serializers

from apps.locations.models import Alert, Location, WaterQualityData


class WaterQualityDataSerializer(serializers.ModelSerializer):
    """Serializer for water quality data."""

    class Meta:
        model = WaterQualityData
        fields = [
            "id",
            "sample_date",
            "ecoli_value",
            "enterococci_value",
            "quality_status",
            "classification_year",
            "is_current",
        ]


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for alerts."""

    class Meta:
        model = Alert
        fields = [
            "id",
            "alert_type",
            "title_en",
            "title_ga",
            "message_en",
            "message_ga",
            "start_date",
            "end_date",
            "is_active",
            "is_season_long",
        ]


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for locations."""

    local_authority_name = serializers.CharField(
        source="local_authority.name",
        read_only=True,
    )
    current_water_quality = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()
    facilities = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = [
            "id",
            "name_en",
            "name_ga",
            "beaches_ie_id",
            "classification",
            "latitude",
            "longitude",
            "local_authority_name",
            "is_active",
            "current_water_quality",
            "active_alerts",
            "facilities",
        ]

    def get_current_water_quality(self, obj: Location) -> dict | None:
        """Get current water quality data."""
        quality = obj.get_current_water_quality()
        if quality:
            return WaterQualityDataSerializer(quality).data
        return None

    def get_active_alerts(self, obj: Location) -> list[dict]:
        """Get active alerts for the location."""
        alerts = obj.get_active_alerts()
        return AlertSerializer(alerts, many=True).data

    def get_facilities(self, obj: Location) -> dict:
        """Get facilities information."""
        return obj.get_facilities()


class LocationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for location lists."""

    has_alert = serializers.SerializerMethodField()
    quality_status = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = [
            "id",
            "name_en",
            "name_ga",
            "beaches_ie_id",
            "classification",
            "latitude",
            "longitude",
            "has_alert",
            "quality_status",
        ]

    def get_has_alert(self, obj: Location) -> bool:
        """Check if location has active alert."""
        return obj.has_active_alert()

    def get_quality_status(self, obj: Location) -> str | None:
        """Get current quality status."""
        quality = obj.get_current_water_quality()
        return quality.quality_status if quality else None
