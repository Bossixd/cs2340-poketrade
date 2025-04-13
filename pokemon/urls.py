from django.urls import path, include
from . import views

app_name = "pokemon"
urlpatterns = [
    path("list/", views.list, name="list"),
    path("generate/", views.generate, name="generate"),
    path("card/", views.card, name="card"),
    path("create-starter-cards/", views.create_starter_cards, name="create_starter_cards"),
]