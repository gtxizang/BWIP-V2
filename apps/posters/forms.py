"""Forms for the posters application."""

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.locations.models import Location

from .models import Poster, PosterTemplate


class PosterGenerateForm(forms.Form):
    """Form for generating a new poster."""

    location = forms.ModelChoiceField(
        queryset=Location.objects.none(),
        label=_("Location"),
        widget=forms.Select(attrs={"class": "form-select", "id": "location-select"}),
        help_text=_("Select the bathing water location"),
    )
    template = forms.ModelChoiceField(
        queryset=PosterTemplate.objects.filter(is_active=True),
        label=_("Template"),
        widget=forms.Select(attrs={"class": "form-select", "id": "template-select"}),
        help_text=_("Select the poster template"),
    )
    size = forms.ChoiceField(
        choices=Poster.Size.choices,
        initial=Poster.Size.A1,
        label=_("Size"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    orientation = forms.ChoiceField(
        choices=Poster.Orientation.choices,
        initial=Poster.Orientation.PORTRAIT,
        label=_("Orientation"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    language = forms.ChoiceField(
        choices=Poster.Language.choices,
        initial=Poster.Language.EN,
        label=_("Language"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    # Override tracking (hidden fields populated by JavaScript)
    recommended_template_code = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"id": "recommended-template-code-input"}),
    )
    override_reason = forms.CharField(
        required=False,
        label=_("Override Reason"),
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "id": "override-reason-input",
            "rows": 3,
            "placeholder": _("e.g., Local knowledge of water conditions, recent incident not yet in EPA data..."),
        }),
        help_text=_("Required when selecting a different template than recommended"),
    )

    # Custom notification
    custom_notification = forms.CharField(
        required=False,
        label=_("Custom Notification"),
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "id": "custom-notification-input",
            "rows": 2,
            "placeholder": _("Optional: Add a custom alert or message to display on the poster"),
        }),
        help_text=_("This message will appear prominently on the poster"),
    )

    def __init__(self, *args, organisation=None, **kwargs) -> None:
        """Initialize form with organisation-filtered locations."""
        super().__init__(*args, **kwargs)
        if organisation:
            self.fields["location"].queryset = Location.objects.filter(
                local_authority=organisation,
                is_active=True,
            ).order_by("name_en")

    def clean(self) -> dict:
        """Validate template matches location classification and override has reason."""
        cleaned_data = super().clean()
        location = cleaned_data.get("location")
        template = cleaned_data.get("template")
        recommended_code = cleaned_data.get("recommended_template_code")
        override_reason = cleaned_data.get("override_reason", "").strip()

        if location and template:
            # Validate classification match
            if location.classification != template.classification:
                raise forms.ValidationError(
                    _(
                        "Template classification (%(template)s) doesn't match "
                        "location classification (%(location)s)"
                    )
                    % {
                        "template": template.get_classification_display(),
                        "location": location.get_classification_display(),
                    }
                )

            # Require override reason if template differs from recommended
            if recommended_code and template.code != recommended_code:
                if not override_reason:
                    raise forms.ValidationError(
                        _("Please provide a reason for overriding the recommended template. "
                          "This is required for audit purposes.")
                    )

        return cleaned_data


class PosterSearchForm(forms.Form):
    """Form for searching/filtering posters."""

    search = forms.CharField(
        label=_("Search"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Search by location..."),
                "class": "form-control",
            }
        ),
    )
    template = forms.ModelChoiceField(
        queryset=PosterTemplate.objects.filter(is_active=True),
        required=False,
        label=_("Template"),
        widget=forms.Select(attrs={"class": "form-select"}),
        empty_label=_("All Templates"),
    )
    size = forms.ChoiceField(
        choices=[("", _("All Sizes"))] + list(Poster.Size.choices),
        required=False,
        label=_("Size"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(
        required=False,
        label=_("From Date"),
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )
    date_to = forms.DateField(
        required=False,
        label=_("To Date"),
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        ),
    )
