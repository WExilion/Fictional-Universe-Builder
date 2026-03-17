from django.urls import path, include

from characters import views

app_name = 'characters'
urlpatterns = [
    path('', views.CharacterListView.as_view(), name='list'),
    path('create/', views.CharacterCreateView.as_view(), name='create'),
    path('<slug:universe_slug>/<slug:slug>/', include([
        path('', views.CharacterDetailView.as_view(), name='detail'),
        path('update/', views.CharacterUpdateView.as_view(), name='update'),
        path('delete/', views.CharacterDeleteView.as_view(), name='delete'),
    ])),
]
