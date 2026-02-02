"""Admin configuration for the posters application."""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Poster, PosterSection, PosterTemplate


@admin.register(PosterTemplate)
class PosterTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for PosterTemplate model."""

    list_display = ("code", "name", "classification", "is_active")
    list_filter = ("classification", "is_active")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(Poster)
class PosterAdmin(admin.ModelAdmin):
    """Admin configuration for Poster model."""

    list_display = (
        "location",
        "template",
        "poster_type",
        "size",
        "language",
        "generated_at",
        "generated_by",
        "pdf_link",
    )
    list_filter = ("template", "poster_type", "size", "language", "published_to_ckan")
    search_fields = ("location__name_en", "location__name_ga")
    raw_id_fields = ("location", "generated_by")
    readonly_fields = ("generated_at", "created_at", "updated_at")
    date_hierarchy = "generated_at"

    fieldsets = (
        (
            None,
            {"fields": ("location", "template", "poster_type")},
        ),
        (
            _("Settings"),
            {"fields": ("size", "orientation", "language")},
        ),
        (
            _("Files"),
            {"fields": ("pdf_file", "preview_image")},
        ),
        (
            _("Data"),
            {
                "fields": ("water_quality_data", "supplementary_content"),
                "classes": ("collapse",),
            },
        ),
        (
            _("Publishing"),
            {"fields": ("published_to_ckan", "ckan_resource_id")},
        ),
        (
            _("Metadata"),
            {
                "fields": ("generated_by", "generated_at", "created_at", "updated_at"),
            },
        ),
    )

    def pdf_link(self, obj: Poster) -> str:
        """Display a link to the PDF file."""
        if obj.pdf_file:
            return format_html(
                '<a href="{}" target="_blank">Download</a>',
                obj.pdf_file.url,
            )
        return "-"

    pdf_link.short_description = _("PDF")


@admin.register(PosterSection)
class PosterSectionAdmin(admin.ModelAdmin):
    """Admin configuration for PosterSection model."""

    list_display = ("poster", "section_type", "generated_at")
    list_filter = ("section_type",)
    raw_id_fields = ("poster",)
    readonly_fields = ("generated_at", "created_at", "updated_at")
