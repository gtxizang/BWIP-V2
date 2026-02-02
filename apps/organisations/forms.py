"""Forms for the organisations application."""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import LocalAuthority


class LocalAuthorityForm(forms.ModelForm):
    """Form for editing Local Authority details."""

    class Meta:
        model = LocalAuthority
        fields = [
            "name",
            "code",
            "contact_email",
            "email_domain",
            "phone",
            "address",
            "website",
            "logo",
            "primary_colour",
            "secondary_colour",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "contact_email": forms.EmailInput(attrs={"class": "form-control"}),
            "email_domain": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "website": forms.URLInput(attrs={"class": "form-control"}),
            "logo": forms.FileInput(attrs={"class": "form-control"}),
            "primary_colour": forms.TextInput(
                attrs={"class": "form-control", "type": "color"}
            ),
            "secondary_colour": forms.TextInput(
                attrs={"class": "form-control", "type": "color"}
            ),
        }
