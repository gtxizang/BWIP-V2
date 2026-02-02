"""
Views for the posters application.

Handles poster generation wizard, dashboard, and history.
"""

import json
import logging
from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.db.models import Prefetch, QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, FormView, ListView, TemplateView

from apps.audit.models import AuditLog
from apps.core.views import OrganisationPermissionMixin
from apps.locations.models import Alert, Location, WaterQualityData
from services.beaches_api.client import BeachesAPIClient
from services.pdf_generation.generator import PosterPDFGenerator
from services.pdf_generation.templates import recommend_template

from .forms import PosterGenerateForm
from .models import Poster, PosterTemplate

logger = logging.getLogger(__name__)


class DashboardView(LoginRequiredMixin, OrganisationPermissionMixin, TemplateView):
    """
    Main dashboard showing map and recent posters.

    Displays an interactive map of bathing water locations and
    a list of recently generated posters.
    """

    template_name = "posters/dashboard.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add dashboard data to context."""
        context = super().get_context_data(**kwargs)
        organisation = self.get_organisation()

        # Get locations for map
        locations = Location.objects.filter(
            local_authority=organisation,
            is_active=True,
        ).prefetch_related(
            Prefetch(
                "water_quality_data",
                queryset=WaterQualityData.objects.filter(is_current=True),
            ),
            Prefetch(
                "alerts",
                queryset=Alert.objects.filter(is_active=True),
            ),
        )

        # Prepare map data
        map_data = []
        for loc in locations:
            current_quality = loc.get_current_water_quality()
            map_data.append(
                {
                    "id": loc.id,
                    "name": loc.name_en,
                    "lat": float(loc.latitude),
                    "lng": float(loc.longitude),
                    "classification": loc.classification,
                    "has_alert": loc.has_active_alert(),
                    "quality_status": (
                        current_quality.quality_status if current_quality else None
                    ),
                }
            )

        context["map_data"] = json.dumps(map_data)
        context["locations"] = locations

        # Get recent posters
        context["recent_posters"] = Poster.objects.filter(
            location__local_authority=organisation,
        ).select_related("location", "template", "generated_by")[:10]

        # Get counts
        context["location_count"] = locations.count()
        context["poster_count"] = Poster.objects.filter(
            location__local_authority=organisation,
        ).count()

        return context


class PosterGenerateView(LoginRequiredMixin, OrganisationPermissionMixin, FormView):
    """
    Poster generation wizard.

    Multi-step form for generating new posters with location selection,
    template recommendation, and customisation options.
    """

    template_name = "posters/generate.html"
    form_class = PosterGenerateForm
    success_url = reverse_lazy("posters:dashboard")

    def get_form_kwargs(self) -> dict[str, Any]:
        """Pass organisation to form."""
        kwargs = super().get_form_kwargs()
        kwargs["organisation"] = self.get_organisation()
        return kwargs

    def get_initial(self) -> dict[str, Any]:
        """Pre-populate location from query parameter."""
        initial = super().get_initial()
        location_id = self.request.GET.get("location")
        if location_id:
            try:
                location = Location.objects.get(
                    pk=location_id,
                    local_authority=self.get_organisation(),
                    is_active=True,
                )
                initial["location"] = location
            except Location.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add pre-selected location ID for JavaScript."""
        context = super().get_context_data(**kwargs)
        context["preselected_location_id"] = self.request.GET.get("location", "")
        return context

    def form_valid(self, form) -> HttpResponse:
        """Generate the poster PDF."""
        location = form.cleaned_data["location"]
        template = form.cleaned_data["template"]
        size = form.cleaned_data["size"]
        orientation = form.cleaned_data["orientation"]
        language = form.cleaned_data["language"]
        recommended_code = form.cleaned_data.get("recommended_template_code", "")
        override_reason = form.cleaned_data.get("override_reason", "").strip()
        custom_notification = form.cleaned_data.get("custom_notification", "").strip()

        try:
            # Fetch EPA data
            api_client = BeachesAPIClient()
            epa_data = api_client.format_for_poster(location.beaches_ie_id)

            # Add custom notification to EPA data for PDF generation
            if custom_notification:
                epa_data["custom_notification"] = custom_notification

            # Generate PDF
            generator = PosterPDFGenerator()
            pdf_bytes = generator.generate_poster(
                location=location,
                template_type=template.code,
                size=size,
                orientation=orientation,
                language=language,
                epa_data=epa_data,
                user=self.request.user,
            )

            # Determine if template was overridden
            template_was_overridden = bool(recommended_code and template.code != recommended_code)
            recommended_template = None
            if recommended_code:
                recommended_template = PosterTemplate.objects.filter(code=recommended_code).first()

            # Create poster record
            poster = Poster.objects.create(
                location=location,
                template=template,
                poster_type=Poster.PosterType.FULL,
                size=size,
                orientation=orientation,
                language=language,
                water_quality_data=epa_data,
                generated_by=self.request.user,
                # Override tracking
                recommended_template=recommended_template,
                template_was_overridden=template_was_overridden,
                override_reason=override_reason if template_was_overridden else "",
                # Custom notification
                custom_notification=custom_notification,
            )

            # Save PDF file
            filename = poster.filename
            poster.pdf_file.save(filename, ContentFile(pdf_bytes))
            poster.save()

            # Build audit details
            audit_details = {
                "template": template.code,
                "size": size,
                "language": language,
            }
            if template_was_overridden:
                audit_details["recommended_template"] = recommended_code
                audit_details["override_reason"] = override_reason
            if custom_notification:
                audit_details["custom_notification"] = custom_notification

            # Log the generation
            AuditLog.objects.create(
                user=self.request.user,
                action=AuditLog.Action.POSTER_GENERATED,
                location=location,
                poster=poster,
                details=audit_details,
            )

            messages.success(self.request, _("Poster generated successfully!"))
            return redirect("posters:detail", pk=poster.pk)

        except Exception as e:
            logger.exception("Error generating poster")
            messages.error(self.request, _("Error generating poster: %(error)s") % {"error": str(e)})
            return self.form_invalid(form)


class PosterDetailView(LoginRequiredMixin, OrganisationPermissionMixin, DetailView):
    """
    View a generated poster with download options.
    """

    model = Poster
    template_name = "posters/detail.html"
    context_object_name = "poster"

    def get_queryset(self) -> QuerySet[Poster]:
        """Filter to user's organisation."""
        return (
            super()
            .get_queryset()
            .filter(location__local_authority=self.get_organisation())
            .select_related("location", "template", "generated_by")
        )


class PosterHistoryView(LoginRequiredMixin, OrganisationPermissionMixin, ListView):
    """
    List all generated posters for the organisation.
    """

    model = Poster
    template_name = "posters/history.html"
    context_object_name = "posters"
    paginate_by = 20

    def get_queryset(self) -> QuerySet[Poster]:
        """Filter posters to user's organisation."""
        return (
            super()
            .get_queryset()
            .filter(location__local_authority=self.get_organisation())
            .select_related("location", "template", "generated_by")
            .order_by("-generated_at")
        )


class TemplateRecommendationView(LoginRequiredMixin, OrganisationPermissionMixin, View):
    """
    API endpoint for template recommendation.

    Returns recommended template based on location's current status.
    """

    def get(self, request: HttpRequest, location_id: int) -> JsonResponse:
        """Get template recommendation for a location."""
        location = get_object_or_404(
            Location,
            pk=location_id,
            local_authority=self.get_organisation(),
        )

        # Fetch current EPA data
        api_client = BeachesAPIClient()
        epa_data = api_client.format_for_poster(location.beaches_ie_id)

        # Get recommendation
        has_alert = epa_data.get("has_active_alerts", False)
        alert_details = epa_data.get("alert_details", {})
        is_season_long = alert_details.get("is_season_long", False)

        recommendation = recommend_template(
            classification=location.classification,
            has_active_alert=has_alert,
            alert_is_season_long=is_season_long,
        )

        # Get available templates for this classification
        templates = PosterTemplate.objects.filter(
            classification=location.classification,
            is_active=True,
        )

        return JsonResponse(
            {
                "recommended_template": recommendation.recommended.value,
                "recommendation_reason": recommendation.reason,
                "can_override": recommendation.can_override,
                "templates": [
                    {"id": t.pk, "code": t.code, "name": t.name, "description": t.description}
                    for t in templates
                ],
                "epa_data": epa_data,
            }
        )


class PosterDownloadView(LoginRequiredMixin, OrganisationPermissionMixin, View):
    """
    Download a generated poster PDF.
    """

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Serve the poster PDF file."""
        poster = get_object_or_404(
            Poster,
            pk=pk,
            location__local_authority=self.get_organisation(),
        )

        if not poster.pdf_file:
            messages.error(request, _("PDF file not found."))
            return redirect("posters:detail", pk=pk)

        response = HttpResponse(
            poster.pdf_file.read(),
            content_type="application/pdf",
        )
        response["Content-Disposition"] = f'attachment; filename="{poster.filename}"'
        return response
