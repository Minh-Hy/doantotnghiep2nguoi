from django.urls import path

from .views import AttemptDetailView, AttemptListCreateView, ContextListView, HealthView, LoginView, LogoutView, ReadinessView


urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("ready/", ReadinessView.as_view(), name="ready"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("contexts/", ContextListView.as_view(), name="context-list"),
    path("attempts/", AttemptListCreateView.as_view(), name="attempt-list-create"),
    path("attempts/<uuid:attempt_id>/", AttemptDetailView.as_view(), name="attempt-detail"),
]
