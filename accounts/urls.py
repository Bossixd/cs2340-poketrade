# accounts/urls.py

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    path('users/<int:user_id>/unban/', views.unban_user, name='unban_user'),
]
