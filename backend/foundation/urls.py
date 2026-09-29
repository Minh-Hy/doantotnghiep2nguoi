from django.urls import path

from .views import (
    AttemptDetailView, AttemptListCreateView, ContextListView,
    HealthView, LoginView, LogoutView, ReadyView,
)

urlpatterns = [
    path('health/', HealthView.as_view(), name='health'),
    path('ready/', ReadyView.as_view(), name='ready'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('contexts/', ContextListView.as_view(), name='contexts'),
    path('attempts/', AttemptListCreateView.as_view(), name='attempts'),
    path('attempts/<uuid:attempt_id>/', AttemptDetailView.as_view(), name='attempt-detail'),
]
