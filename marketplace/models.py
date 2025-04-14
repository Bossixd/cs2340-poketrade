# marketplace/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Profile, ProfileCards
from pokemon.models import Card

from django.contrib.auth.models import User
from pokemon.models import Card
from accounts.models import Profile, ProfileCards


class ElementType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class CardListing(models.Model):
    seller = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='listings')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    price = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(999999)
        ]
    )
    listed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

class DesiredCard(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='desired_card')
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True, blank=True)
    pity_counter = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.card.pokemon_info.name} card by {self.seller.user.username} for {self.price} coins"

    # class Meta:
    #     ordering = ['-listed_at']

    @property
    def profile_card(self):
        """Returns the ProfileCards instance connecting this listing's seller to the card"""
        return ProfileCards.objects.filter(profile=self.seller, cards=self.card).first()

    def increase_pity(self):
        self.pity_counter += 1
        self.save()

    def reset_pity(self):
        self.pity_counter = 0
        self.save()