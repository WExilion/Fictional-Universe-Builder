from django.urls import path, include

from stories import views

app_name = 'stories'

urlpatterns = [
    path('', views.StoryListView.as_view(), name='list'),
    path('create/', views.StoryCreateView.as_view(), name='create'),
    path('<slug:universe_slug>/<slug:slug>/', include([
        path('', views.StoryDetailView.as_view(), name='detail'),
        path('update/', views.StoryUpdateView.as_view(), name='update'),
        path('delete/', views.StoryDeleteView.as_view(), name='delete'),
    ])),
]