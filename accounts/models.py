from django.db import models
from django.contrib.auth.models import User
from pokemon.models import Card
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_banned = models.BooleanField(default=False)
    currency = models.PositiveIntegerField(default=1000)

    def __str__(self):
        return f"Profile for {self.user.username} (Currency: {self.currency})"


class ProfileCards(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    cards = models.ForeignKey(Card, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.profile.user.username}'s {self.cards.pokemon_info.name} Card"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile
    """
    if created:
        Profile.objects.get_or_create(user=instance)
    else:
        # Only save the profile if it exists
        try:
            if hasattr(instance, 'profile'):
                instance.profile.save()
        except Profile.DoesNotExist:
            pass