from django.urls import path, include
from . import views

app_name = "pokemon"
urlpatterns = [
    path("list/", views.list, name="list"),
    path("generate/", views.generate, name="generate"),
    path("generate/create/", views.generate_create, name="generate_create"),

]