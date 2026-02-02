"""
Location models for BWIP.

Provides models for bathing water locations, water quality data,
and alerts from the EPA beaches.ie API.
"""

from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import NamedModel, TimeStampedModel


class Location(TimeStampedModel, NamedModel):
    """
    Represents a bathing water location.

    Each location belongs to exactly one Local Authority and has
    associated water quality data and alerts from beaches.ie.

    Example:
        >>> location = Location.objects.create(
        ...     name_en="Dollymount Strand",
        ...     name_ga="Tra Dhollymount",
        ...     local_authority=dcc,
        ...     beaches_ie_id="IEWEBWC170_0000_0200",
        ...     classification=Location.Classification.IDENTIFIED,
        ...     latitude=Decimal("53.2695"),
        ...     longitude=Decimal("-6.1544"),
        ... )
    """

    class Classification(models.TextChoices):
        """Bathing water classification types."""

        IDENTIFIED = "IDENTIFIED", _("Identified Bathing Water")
        NON_IDENTIFIED = "NON_IDENTIFIED", _("Non-Identified Bathing Water")

    local_authority = models.ForeignKey(
        "organisations.LocalAuthority",
        on_delete=models.PROTECT,
        related_name="locations",
        verbose_name=_("local authority"),
    )
    beaches_ie_id = models.CharField(
        _("beaches.ie ID"),
        max_length=50,
        unique=True,
        help_text=_("Unique identifier from beaches.ie API, e.g., 'IEWEBWC170_0000_0200'"),
    )
    classification = models.CharField(
        _("classification"),
        max_length=20,
        choices=Classification.choices,
        default=Classification.IDENTIFIED,
    )
    latitude = models.DecimalField(
        _("latitude"),
        max_digits=9,
        decimal_places=6,
    )
    longitude = models.DecimalField(
        _("longitude"),
        max_digits=9,
        decimal_places=6,
    )
    description_en = models.TextField(
        _("description (English)"),
        blank=True,
        help_text=_("Description of the location in English"),
    )
    description_ga = models.TextField(
        _("description (Irish)"),
        blank=True,
        help_text=_("Description of the location in Irish"),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
    )

    # Facilities
    has_toilets = models.BooleanField(_("toilets"), default=False)
    has_parking = models.BooleanField(_("parking"), default=False)
    has_lifeguard = models.BooleanField(_("lifeguard"), default=False)
    has_disability_access = models.BooleanField(_("disability access"), default=False)
    has_blue_flag = models.BooleanField(_("blue flag"), default=False)
    dogs_allowed = models.BooleanField(_("dogs allowed"), default=True)

    class Meta:
        verbose_name = _("location")
        verbose_name_plural = _("locations")
        ordering = ["name_en"]
        indexes = [
            models.Index(fields=["local_authority", "is_active"]),
            models.Index(fields=["beaches_ie_id"]),
            models.Index(fields=["classification"]),
        ]

    def __str__(self) -> str:
        """Return the location name."""
        return self.name_en

    @property
    def coordinates(self) -> tuple[float, float]:
        """Return coordinates as (latitude, longitude) tuple."""
        return (float(self.latitude), float(self.longitude))

    @property
    def is_identified(self) -> bool:
        """Check if this is an identified bathing water."""
        return self.classification == self.Classification.IDENTIFIED

    def get_current_water_quality(self) -> "WaterQualityData | None":
        """Get the most recent water quality data."""
        return self.water_quality_data.filter(is_current=True).first()

    def get_active_alerts(self):
        """Get all currently active alerts for this location."""
        return self.alerts.filter(is_active=True)

    def has_active_alert(self) -> bool:
        """Check if there's any active alert for this location."""
        return self.alerts.filter(is_active=True).exists()

    def get_facilities(self) -> dict[str, bool]:
        """Get a dictionary of all facilities and their availability."""
        return {
            "toilets": self.has_toilets,
            "parking": self.has_parking,
            "lifeguard": self.has_lifeguard,
            "disability_access": self.has_disability_access,
            "blue_flag": self.has_blue_flag,
            "dogs_allowed": self.dogs_allowed,
        }


class WaterQualityData(TimeStampedModel):
    """
    Water quality measurement data from beaches.ie.

    Stores E. coli and Enterococci measurements along with
    overall quality classification.

    Example:
        >>> quality = WaterQualityData.objects.create(
        ...     location=location,
        ...     sample_date=date(2024, 7, 15),
        ...     ecoli_value=50,
        ...     enterococci_value=30,
        ...     quality_status="EXCELLENT",
        ...     is_current=True,
        ... )
    """

    class QualityStatus(models.TextChoices):
        """Water quality status classifications."""

        EXCELLENT = "EXCELLENT", _("Excellent")
        GOOD = "GOOD", _("Good")
        SUFFICIENT = "SUFFICIENT", _("Sufficient")
        POOR = "POOR", _("Poor")
        NOT_CLASSIFIED = "NOT_CLASSIFIED", _("Not Classified")

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="water_quality_data",
        verbose_name=_("location"),
    )
    sample_date = models.DateField(
        _("sample date"),
        db_index=True,
    )
    ecoli_value = models.IntegerField(
        _("E. coli value"),
        null=True,
        blank=True,
        help_text=_("E. coli count (cfu/100ml)"),
    )
    enterococci_value = models.IntegerField(
        _("Enterococci value"),
        null=True,
        blank=True,
        help_text=_("Intestinal Enterococci count (cfu/100ml)"),
    )
    quality_status = models.CharField(
        _("quality status"),
        max_length=20,
        choices=QualityStatus.choices,
        default=QualityStatus.NOT_CLASSIFIED,
    )
    classification_year = models.IntegerField(
        _("classification year"),
        null=True,
        blank=True,
        help_text=_("Year of the water quality classification"),
    )
    is_current = models.BooleanField(
        _("is current"),
        default=False,
        help_text=_("Whether this is the most recent measurement"),
    )
    raw_data = models.JSONField(
        _("raw data"),
        default=dict,
        blank=True,
        help_text=_("Raw data from beaches.ie API"),
    )

    class Meta:
        verbose_name = _("water quality data")
        verbose_name_plural = _("water quality data")
        ordering = ["-sample_date"]
        indexes = [
            models.Index(fields=["location", "-sample_date"]),
            models.Index(fields=["location", "is_current"]),
        ]
        get_latest_by = "sample_date"

    def __str__(self) -> str:
        """Return a string representation of the measurement."""
        return f"{self.location.name_en} - {self.sample_date} ({self.quality_status})"

    def save(self, *args, **kwargs) -> None:
        """Ensure only one current record per location."""
        if self.is_current:
            # Set all other records for this location to not current
            WaterQualityData.objects.filter(
                location=self.location, is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Alert(TimeStampedModel):
    """
    Bathing water alert or advisory from beaches.ie.

    Stores notices, restrictions, or advisories for locations.

    Example:
        >>> alert = Alert.objects.create(
        ...     location=location,
        ...     alert_type=Alert.AlertType.NOTICE,
        ...     title_en="Temporary Advisory",
        ...     message_en="Swimming not advised due to recent rainfall",
        ...     start_date=date(2024, 7, 15),
        ...     is_active=True,
        ... )
    """

    class AlertType(models.TextChoices):
        """Types of bathing water alerts."""

        NOTICE = "NOTICE", _("Notice")
        ADVISORY = "ADVISORY", _("Advisory")
        RESTRICTION = "RESTRICTION", _("Restriction")
        CLOSURE = "CLOSURE", _("Closure")

    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="alerts",
        verbose_name=_("location"),
    )
    alert_type = models.CharField(
        _("alert type"),
        max_length=20,
        choices=AlertType.choices,
        default=AlertType.NOTICE,
    )
    title_en = models.CharField(
        _("title (English)"),
        max_length=200,
    )
    title_ga = models.CharField(
        _("title (Irish)"),
        max_length=200,
        blank=True,
    )
    message_en = models.TextField(
        _("message (English)"),
    )
    message_ga = models.TextField(
        _("message (Irish)"),
        blank=True,
    )
    start_date = models.DateField(
        _("start date"),
    )
    end_date = models.DateField(
        _("end date"),
        null=True,
        blank=True,
        help_text=_("Leave blank for ongoing alerts"),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
    )
    is_season_long = models.BooleanField(
        _("season long"),
        default=False,
        help_text=_("Whether this is a season-long restriction"),
    )
    beaches_ie_id = models.CharField(
        _("beaches.ie alert ID"),
        max_length=50,
        blank=True,
        help_text=_("Original alert ID from beaches.ie"),
    )
    raw_data = models.JSONField(
        _("raw data"),
        default=dict,
        blank=True,
        help_text=_("Raw data from beaches.ie API"),
    )

    class Meta:
        verbose_name = _("alert")
        verbose_name_plural = _("alerts")
        ordering = ["-start_date", "-created_at"]
        indexes = [
            models.Index(fields=["location", "is_active"]),
            models.Index(fields=["start_date", "end_date"]),
        ]

    def __str__(self) -> str:
        """Return a string representation of the alert."""
        return f"{self.location.name_en} - {self.title_en}"

    def get_title(self, language: str = "en") -> str:
        """Get title in the specified language."""
        if language == "ga" and self.title_ga:
            return self.title_ga
        return self.title_en

    def get_message(self, language: str = "en") -> str:
        """Get message in the specified language."""
        if language == "ga" and self.message_ga:
            return self.message_ga
        return self.message_en
