"""
Forms for the accounts application.

Provides forms for profile management.
Authentication forms are handled by django-allauth.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """
    Form for editing user profile information.

    Allows users to update their profile details including name and phone.
    """

    first_name = forms.CharField(
        label=_("First Name"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        label=_("Last Name"),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = UserProfile
        fields = ["phone"]
        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form with user data."""
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["first_name"].initial = self.instance.user.first_name
            self.fields["last_name"].initial = self.instance.user.last_name

    def save(self, commit: bool = True) -> UserProfile:
        """Save the profile and update related User fields."""
        profile = super().save(commit=False)
        if profile.user:
            profile.user.first_name = self.cleaned_data["first_name"]
            profile.user.last_name = self.cleaned_data["last_name"]
            if commit:
                profile.user.save()
        if commit:
            profile.save()
        return profile
