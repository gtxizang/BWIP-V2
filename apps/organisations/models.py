"""
Organisation models for BWIP.

Provides Local Authority model for multi-tenancy support
across Irish Local Authorities.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import TimeStampedModel


class LocalAuthority(TimeStampedModel):
    """
    Represents an Irish Local Authority (County/City Council).

    Each Local Authority can have multiple users and locations.
    Users are linked via UserProfile.local_authority FK.

    Example:
        >>> la = LocalAuthority.objects.create(
        ...     name="Dublin City Council",
        ...     code="DCC",
        ...     email_domain="dublincity.ie",
        ...     contact_email="env@dublincity.ie",
        ... )
    """

    name = models.CharField(
        _("name"),
        max_length=200,
        help_text=_("Full name of the Local Authority"),
    )
    code = models.CharField(
        _("code"),
        max_length=10,
        unique=True,
        help_text=_("Short code, e.g., 'DCC' for Dublin City Council"),
    )
    email_domain = models.CharField(
        _("email domain"),
        max_length=100,
        blank=True,
        help_text=_("Allowed email domain, e.g., 'dublincity.ie'"),
    )
    contact_email = models.EmailField(
        _("contact email"),
        blank=True,
        help_text=_("Primary contact email for the Local Authority"),
    )
    logo = models.ImageField(
        _("logo"),
        upload_to="logos/",
        blank=True,
        help_text=_("Local Authority logo for posters"),
    )
    primary_colour = models.CharField(
        _("primary colour"),
        max_length=7,
        default="#0066CC",
        help_text=_("Hex colour code for branding, e.g., '#0066CC'"),
    )
    secondary_colour = models.CharField(
        _("secondary colour"),
        max_length=7,
        default="#FFFFFF",
        help_text=_("Secondary hex colour code for branding"),
    )
    address = models.TextField(
        _("address"),
        blank=True,
        help_text=_("Physical address of the Local Authority"),
    )
    website = models.URLField(
        _("website"),
        blank=True,
        help_text=_("Official website URL"),
    )
    phone = models.CharField(
        _("phone"),
        max_length=20,
        blank=True,
        help_text=_("Contact phone number"),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Whether this Local Authority is active"),
    )

    class Meta:
        verbose_name = _("local authority")
        verbose_name_plural = _("local authorities")
        ordering = ["name"]

    def __str__(self) -> str:
        """Return the Local Authority name."""
        return self.name

    @property
    def short_name(self) -> str:
        """Get a shortened version of the name."""
        return self.code

    def get_active_users_count(self) -> int:
        """Get count of active users in this organisation."""
        return self.user_profiles.filter(user__is_active=True).count()

    def get_locations_count(self) -> int:
        """Get count of locations belonging to this organisation."""
        return self.locations.filter(is_active=True).count()


# Irish Local Authority codes for reference
IRISH_LOCAL_AUTHORITIES = [
    ("CE", "Clare County Council"),
    ("CN", "Cavan County Council"),
    ("CO", "Cork County Council"),
    ("CW", "Carlow County Council"),
    ("DCC", "Dublin City Council"),
    ("DL", "Donegal County Council"),
    ("DLRCC", "Dun Laoghaire-Rathdown County Council"),
    ("FCC", "Fingal County Council"),
    ("GY", "Galway County Council"),
    ("KE", "Kildare County Council"),
    ("KK", "Kilkenny County Council"),
    ("KY", "Kerry County Council"),
    ("LD", "Longford County Council"),
    ("LH", "Louth County Council"),
    ("LK", "Limerick City and County Council"),
    ("LM", "Leitrim County Council"),
    ("LS", "Laois County Council"),
    ("MH", "Meath County Council"),
    ("MN", "Monaghan County Council"),
    ("MO", "Mayo County Council"),
    ("OY", "Offaly County Council"),
    ("RN", "Roscommon County Council"),
    ("SDCC", "South Dublin County Council"),
    ("SO", "Sligo County Council"),
    ("TA", "Tipperary County Council"),
    ("WD", "Waterford City and County Council"),
    ("WH", "Westmeath County Council"),
    ("WX", "Wexford County Council"),
    ("WW", "Wicklow County Council"),
]
