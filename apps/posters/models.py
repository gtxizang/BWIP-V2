"""
Poster models for BWIP.

Provides models for poster templates and generated posters.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class PosterTemplate(TimeStampedModel):
    """
    Poster template configuration.

    Defines the available poster templates (1A, 1B, 1C, 2A, 2B)
    per EPA specifications.

    Example:
        >>> template = PosterTemplate.objects.create(
        ...     code="1A",
        ...     name="Identified - No Restrictions",
        ...     classification=PosterTemplate.Classification.IDENTIFIED,
        ... )
    """

    class TemplateCode(models.TextChoices):
        """Template codes per EPA specifications."""

        T1A = "1A", _("1A - Identified, No Restrictions")
        T1B = "1B", _("1B - Identified, Temporary Restrictions")
        T1C = "1C", _("1C - Identified, Season-Long Restrictions")
        T2A = "2A", _("2A - Non-Identified, With Restrictions")
        T2B = "2B", _("2B - Non-Identified, No Restrictions")

    class Classification(models.TextChoices):
        """Classification types for templates."""

        IDENTIFIED = "IDENTIFIED", _("Identified Bathing Water")
        NON_IDENTIFIED = "NON_IDENTIFIED", _("Non-Identified Bathing Water")

    code = models.CharField(
        _("code"),
        max_length=5,
        choices=TemplateCode.choices,
        unique=True,
    )
    name = models.CharField(
        _("name"),
        max_length=100,
    )
    description = models.TextField(
        _("description"),
        blank=True,
        help_text=_("Description of when this template should be used"),
    )
    classification = models.CharField(
        _("classification"),
        max_length=20,
        choices=Classification.choices,
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
    )

    class Meta:
        verbose_name = _("poster template")
        verbose_name_plural = _("poster templates")
        ordering = ["code"]

    def __str__(self) -> str:
        """Return template code and name."""
        return f"{self.code} - {self.name}"


class Poster(TimeStampedModel):
    """
    Generated poster record.

    Stores information about each generated poster including
    the PDF file, settings used, and EPA data at time of generation.

    Example:
        >>> poster = Poster.objects.create(
        ...     location=location,
        ...     template=template,
        ...     poster_type=Poster.PosterType.FULL,
        ...     size=Poster.Size.A1,
        ...     orientation=Poster.Orientation.PORTRAIT,
        ...     language=Poster.Language.EN,
        ...     generated_by=user,
        ... )
    """

    class PosterType(models.TextChoices):
        """Types of poster generations."""

        FULL = "FULL", _("Full Poster")
        SECTION = "SECTION", _("Section Update")

    class Size(models.TextChoices):
        """Available poster sizes."""

        A1 = "A1", _("A1 (594 x 841 mm)")
        A3 = "A3", _("A3 (297 x 420 mm)")
        A4 = "A4", _("A4 (210 x 297 mm)")
        A5 = "A5", _("A5 (148 x 210 mm)")

    class Orientation(models.TextChoices):
        """Poster orientations."""

        PORTRAIT = "PORTRAIT", _("Portrait")
        LANDSCAPE = "LANDSCAPE", _("Landscape")

    class Language(models.TextChoices):
        """Available languages."""

        EN = "en", _("English")
        GA = "ga", _("Irish")
        BILINGUAL = "bilingual", _("Bilingual")

    location = models.ForeignKey(
        "locations.Location",
        on_delete=models.PROTECT,
        related_name="posters",
        verbose_name=_("location"),
    )
    template = models.ForeignKey(
        PosterTemplate,
        on_delete=models.PROTECT,
        related_name="posters",
        verbose_name=_("template"),
    )
    poster_type = models.CharField(
        _("poster type"),
        max_length=10,
        choices=PosterType.choices,
        default=PosterType.FULL,
    )
    size = models.CharField(
        _("size"),
        max_length=5,
        choices=Size.choices,
        default=Size.A1,
    )
    orientation = models.CharField(
        _("orientation"),
        max_length=10,
        choices=Orientation.choices,
        default=Orientation.PORTRAIT,
    )
    language = models.CharField(
        _("language"),
        max_length=10,
        choices=Language.choices,
        default=Language.EN,
    )

    # Files
    pdf_file = models.FileField(
        _("PDF file"),
        upload_to="posters/%Y/%m/",
        blank=True,
    )
    preview_image = models.ImageField(
        _("preview image"),
        upload_to="previews/%Y/%m/",
        blank=True,
    )

    # Template override tracking
    recommended_template = models.ForeignKey(
        PosterTemplate,
        on_delete=models.PROTECT,
        related_name="recommended_for_posters",
        verbose_name=_("recommended template"),
        null=True,
        blank=True,
        help_text=_("The template that was recommended by the system"),
    )
    template_was_overridden = models.BooleanField(
        _("template was overridden"),
        default=False,
        help_text=_("Whether the user chose a different template than recommended"),
    )
    override_reason = models.TextField(
        _("override reason"),
        blank=True,
        help_text=_("Required justification when overriding the recommended template"),
    )

    # Custom notifications/alerts
    custom_notification = models.TextField(
        _("custom notification"),
        blank=True,
        help_text=_("Custom alert or notification message to display on the poster"),
    )

    # Data snapshot
    water_quality_data = models.JSONField(
        _("water quality data"),
        default=dict,
        help_text=_("EPA data snapshot at time of generation"),
    )
    supplementary_content = models.JSONField(
        _("supplementary content"),
        default=dict,
        blank=True,
        help_text=_("Additional content included in the poster"),
    )

    # Metadata
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="generated_posters",
        verbose_name=_("generated by"),
    )
    generated_at = models.DateTimeField(
        _("generated at"),
        auto_now_add=True,
    )

    # CKAN publishing
    published_to_ckan = models.BooleanField(
        _("published to CKAN"),
        default=False,
    )
    ckan_resource_id = models.CharField(
        _("CKAN resource ID"),
        max_length=100,
        blank=True,
    )

    class Meta:
        verbose_name = _("poster")
        verbose_name_plural = _("posters")
        ordering = ["-generated_at"]
        indexes = [
            models.Index(fields=["location", "-generated_at"]),
            models.Index(fields=["generated_by", "-generated_at"]),
            models.Index(fields=["-generated_at"]),
        ]

    def __str__(self) -> str:
        """Return poster description."""
        return f"{self.location.name_en} - {self.template.code} ({self.size})"

    @property
    def filename(self) -> str:
        """Generate a descriptive filename for the poster."""
        from apps.core.utils import sanitize_filename

        date_str = self.generated_at.strftime("%Y%m%d_%H%M%S")
        return sanitize_filename(
            f"{self.location.name_en}_{self.template.code}_{self.size}_{date_str}.pdf"
        )


class PosterSection(TimeStampedModel):
    """
    Individual section that can be updated on a poster.

    Used for generating small section updates that can be
    applied to existing printed posters.

    Example:
        >>> section = PosterSection.objects.create(
        ...     poster=poster,
        ...     section_type=PosterSection.SectionType.WATER_QUALITY,
        ...     pdf_file=section_pdf,
        ... )
    """

    class SectionType(models.TextChoices):
        """Types of poster sections."""

        WATER_QUALITY = "WATER_QUALITY", _("Water Quality")
        ALERTS = "ALERTS", _("Alerts")
        QR_CODE = "QR_CODE", _("QR Code")
        HEADER = "HEADER", _("Header")
        FOOTER = "FOOTER", _("Footer")

    poster = models.ForeignKey(
        Poster,
        on_delete=models.CASCADE,
        related_name="sections",
        verbose_name=_("poster"),
    )
    section_type = models.CharField(
        _("section type"),
        max_length=20,
        choices=SectionType.choices,
    )
    pdf_file = models.FileField(
        _("PDF file"),
        upload_to="sections/%Y/%m/",
    )
    generated_at = models.DateTimeField(
        _("generated at"),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _("poster section")
        verbose_name_plural = _("poster sections")
        ordering = ["-generated_at"]

    def __str__(self) -> str:
        """Return section description."""
        return f"{self.poster} - {self.section_type}"
