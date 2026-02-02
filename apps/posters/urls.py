"""URL patterns for the posters application."""

from django.urls import path

from . import views

app_name = "posters"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("generate/", views.PosterGenerateView.as_view(), name="generate"),
    path("history/", views.PosterHistoryView.as_view(), name="history"),
    path("poster/<int:pk>/", views.PosterDetailView.as_view(), name="detail"),
    path("poster/<int:pk>/download/", views.PosterDownloadView.as_view(), name="download"),
    path(
        "api/template-recommendation/<int:location_id>/",
        views.TemplateRecommendationView.as_view(),
        name="template_recommendation",
    ),
]
