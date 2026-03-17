from django.urls import path

from common import views

app_name = 'common'
urlpatterns = [
    # path('', views.WelcomeView.as_view(), name="welcome"),
    path('', views.HomeView.as_view(), name="home"),
    # path('', views.HomeView.as_view(), name="welcome"),
    # path('', TemplateView.as_view(), name='home'),

]