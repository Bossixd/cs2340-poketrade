# marketplace/models.py
from django.db import models
from django.contrib.auth.models import User
from pokemon.models import Card
from accounts.models import Profile, ProfileCards


class ElementType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class DesiredCard(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='desired_card')
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True)
    pity_counter = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.profile.user.username}'s desired card: {self.card.pokemon_info.name if self.card else 'None'}"

    def increase_pity(self):
        self.pity_counter += 1
        self.save()

    def reset_pity(self):
        self.pity_counter = 0
        self.save()