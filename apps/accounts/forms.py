"""
Forms for the accounts application.

Provides forms for user authentication and profile management.
"""

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import UserProfile

User = get_user_model()


class EmailAuthenticationForm(AuthenticationForm):
    """
    Authentication form that uses email instead of username.

    Extends Django's AuthenticationForm with email-focused labels and help text.
    """

    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter your email"),
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter your password"),
            }
        ),
    )

    error_messages = {
        "invalid_login": _(
            "Please enter a correct email and password. "
            "Note that both fields may be case-sensitive."
        ),
        "inactive": _("This account is inactive."),
    }


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


class UserCreateForm(UserCreationForm):
    """
    Form for creating new users.

    Used by administrators to create new user accounts.
    """

    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
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
        model = User
        fields = ["email", "first_name", "last_name", "password1", "password2"]

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the form with Bootstrap styling."""
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["class"] = "form-control"
        self.fields["password2"].widget.attrs["class"] = "form-control"

    def save(self, commit: bool = True) -> User:
        """Save the user with email as username."""
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
