from django.contrib.auth import views as auth_views
from django.urls import path, include, reverse_lazy

from accounts import views

app_name = "accounts"

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/', include([
        path('edit/', views.ProfileUpdateView.as_view(), name='edit'),
        path('delete/', views.UserDeleteView.as_view(), name='delete'),

        path('password-change/', include([
            path('', views.CustomPasswordChangeView.as_view(), name='password-change'),
            path('done/', auth_views.PasswordChangeDoneView.as_view(
                template_name='accounts/password-change-done.html'
            ), name='password-change-done'),
        ])),

        path('<int:pk>/', views.ProfileDetailView.as_view(), name='detail'),
    ])),
]