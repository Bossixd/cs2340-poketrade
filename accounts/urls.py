from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # User profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Admin management URLs
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    path('users/<int:user_id>/unban/', views.unban_user, name='unban_user'),
    
    # Currency management
    path('currency/add/', views.add_currency, name='add_currency'),
]