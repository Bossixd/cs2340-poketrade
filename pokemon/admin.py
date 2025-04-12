from django.contrib import admin
from .models import Pokemon, Card

# Register your models here.

@admin.register(Pokemon)
class Pokemon(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(Card)
class Card(admin.ModelAdmin):
    search_fields = ['pokemon_info__name']