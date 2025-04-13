from django.urls import path
from .views import hub_view

app_name = 'pokehub'

urlpatterns = [
    path('', hub_view, name='hub'),
    path('hub/', hub_view, name='hub-alt'),
]