"""URL patterns for the organisations application."""

from django.urls import path

from . import views

app_name = "organisations"

urlpatterns = [
    path("", views.LocalAuthorityListView.as_view(), name="list"),
    path("my-organisation/", views.LocalAuthorityDetailView.as_view(), name="detail"),
]
