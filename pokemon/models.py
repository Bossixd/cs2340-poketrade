from django.db import models
import uuid

# Create your models here.
class Pokemon(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    pokedexNumber = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    @property
    def cards(self):
        """Returns all Card objects related to this Pokemon"""
        return self.card_set.all()
    
class Card(models.Model):
    id = models.AutoField(primary_key=True)
    pokemon_info = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    hp = models.FloatField()
    small_image = models.CharField(max_length=100)
    large_image = models.CharField(max_length=100)
    
    def __str__(self):
        return self.pokemon_info.name