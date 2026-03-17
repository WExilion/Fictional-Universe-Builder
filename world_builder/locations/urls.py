from django.urls import path, include

from locations import views

app_name = 'locations'
urlpatterns = [
    path('', views.LocationListView.as_view(), name='list'),
    path('create/', views.LocationCreateView.as_view(), name='create'),
    path('<slug:universe_slug>/<slug:slug>/', include([
        path('', views.LocationDetailView.as_view(), name='detail'),
        path('update/', views.LocationUpdateView.as_view(), name='update'),
        path('delete/', views.LocationDeleteView.as_view(), name='delete'),
    ])),
]