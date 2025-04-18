from django.urls import path, include
from . import views

app_name = "auths"
urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("pokehub/", views.logout, name="logout"),
    path("reset/", views.reset, name="reset"),
    path('logout/', views.logout, name='logout')
]