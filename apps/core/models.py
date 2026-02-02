"""
Core abstract models for BWIP.

Provides base model classes with common functionality that other
models can inherit from.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """
    Abstract base model with created and updated timestamps.

    Provides automatic tracking of when records are created and modified.
    Inherit from this model when you need timestamp tracking.

    Example:
        >>> class MyModel(TimeStampedModel):
        ...     name = models.CharField(max_length=100)
    """

    created_at = models.DateTimeField(
        _("created at"),
        auto_now_add=True,
        db_index=True,
        help_text=_("When this record was created"),
    )
    updated_at = models.DateTimeField(
        _("updated at"),
        auto_now=True,
        help_text=_("When this record was last updated"),
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteModel(models.Model):
    """
    Abstract base model with soft delete functionality.

    Instead of actually deleting records, marks them as deleted.
    Use the `deleted_at` field to filter out "deleted" records.

    Example:
        >>> class MyModel(SoftDeleteModel):
        ...     name = models.CharField(max_length=100)
        >>> obj = MyModel.objects.create(name="test")
        >>> obj.soft_delete()  # Sets deleted_at instead of deleting
    """

    deleted_at = models.DateTimeField(
        _("deleted at"),
        null=True,
        blank=True,
        db_index=True,
        help_text=_("When this record was soft-deleted (null if not deleted)"),
    )

    class Meta:
        abstract = True

    @property
    def is_deleted(self) -> bool:
        """Check if this record has been soft-deleted."""
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """Mark this record as deleted without actually removing it."""
        from django.utils import timezone

        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])

    def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at"])


class ActiveManager(models.Manager):
    """
    Manager that only returns active (non-deleted) records.

    Use this with SoftDeleteModel to easily filter out deleted records.
    """

    def get_queryset(self) -> models.QuerySet:
        """Return only records that haven't been soft-deleted."""
        return super().get_queryset().filter(deleted_at__isnull=True)


class NamedModel(models.Model):
    """
    Abstract base model for entities with English and Irish names.

    Provides bilingual name support for Irish Local Authority applications.

    Example:
        >>> class Beach(NamedModel):
        ...     latitude = models.DecimalField(...)
    """

    name_en = models.CharField(
        _("name (English)"),
        max_length=200,
        help_text=_("Name in English"),
    )
    name_ga = models.CharField(
        _("name (Irish)"),
        max_length=200,
        blank=True,
        help_text=_("Name in Irish (Gaeilge)"),
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        """Return the English name as the string representation."""
        return self.name_en

    def get_name(self, language: str = "en") -> str:
        """
        Get the name in the specified language.

        Args:
            language: Language code ('en' or 'ga')

        Returns:
            Name in the requested language, falling back to English if Irish not available.
        """
        if language == "ga" and self.name_ga:
            return self.name_ga
        return self.name_en
