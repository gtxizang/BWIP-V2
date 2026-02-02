"""Forms for the locations application."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Location


class LocationSearchForm(forms.Form):
    """Form for searching/filtering locations."""

    search = forms.CharField(
        label=_("Search"),
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": _("Search by name..."),
                "class": "form-control",
            }
        ),
    )
    classification = forms.ChoiceField(
        label=_("Classification"),
        required=False,
        choices=[("", _("All"))] + list(Location.Classification.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    has_alert = forms.ChoiceField(
        label=_("Alert Status"),
        required=False,
        choices=[
            ("", _("All")),
            ("yes", _("Has Active Alert")),
            ("no", _("No Active Alert")),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )


class LocationForm(forms.ModelForm):
    """Form for editing location details."""

    class Meta:
        model = Location
        fields = [
            "name_en",
            "name_ga",
            "description_en",
            "description_ga",
            "classification",
            "latitude",
            "longitude",
            "has_toilets",
            "has_parking",
            "has_lifeguard",
            "has_disability_access",
            "has_blue_flag",
            "dogs_allowed",
            "is_active",
        ]
        widgets = {
            "name_en": forms.TextInput(attrs={"class": "form-control"}),
            "name_ga": forms.TextInput(attrs={"class": "form-control"}),
            "description_en": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "description_ga": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "classification": forms.Select(attrs={"class": "form-select"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.000001"}),
        }
