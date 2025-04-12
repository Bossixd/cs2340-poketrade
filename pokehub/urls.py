from django.urls import path
from . import views

app_name = "pokehub"
urlpatterns = [
    path('hub/', views.main, name='hub'),
]