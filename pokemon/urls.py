from django.urls import path, include
from . import views

app_name = "pokemon"
urlpatterns = [
    path("list/", views.list, name="list"),
    path("generate/", views.generate, name="generate"),
    path("card/", views.card, name="card"),
]