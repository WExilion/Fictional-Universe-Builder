from django.urls import path

from stories.api_views import StoryListCreateApiView, StoryDetailApiView

urlpatterns = [
    path('', StoryListCreateApiView.as_view(), name='api-story-list'),
    path('<slug:universe_slug>/<slug:slug>/', StoryDetailApiView.as_view(), name='api-story-detail'),
]