from django.urls import path

from .views import AttemptDetailView, AttemptListCreateView, ContextListView, HealthView


urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("contexts/", ContextListView.as_view(), name="context-list"),
    path("attempts/", AttemptListCreateView.as_view(), name="attempt-list-create"),
    path("attempts/<uuid:attempt_id>/", AttemptDetailView.as_view(), name="attempt-detail"),
]
