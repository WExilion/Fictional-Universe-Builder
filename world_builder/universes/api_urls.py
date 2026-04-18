from django.urls import path

from universes.api_views import UniverseListCreateApiView, UniverseDetailApiView

urlpatterns = [
    path('', UniverseListCreateApiView.as_view(), name='api-universe-list'),
    path('<slug:slug>/', UniverseDetailApiView.as_view(), name='api-universe-detail'),
]