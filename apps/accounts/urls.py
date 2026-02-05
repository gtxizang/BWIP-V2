"""URL patterns for the accounts application.

Profile views only - authentication is handled by django-allauth.
"""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/edit/", views.ProfileUpdateView.as_view(), name="profile_edit"),
]
