from django.urls import path, include
from universes import views


app_name = 'universes'
urlpatterns = [
    path('', views.UniverseListView.as_view(), name='list'),
    path('create/', views.UniverseCreateView.as_view(), name='create'),
    path('<slug:slug>/', include([
        path('', views.UniverseDetailView.as_view(), name='detail'),
        path('update/', views.UniverseUpdateView.as_view(), name='update'),
        path('delete/', views.UniverseDeleteView.as_view(), name='delete'),
    ])),
]