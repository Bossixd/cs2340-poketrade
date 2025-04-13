# accounts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    # This will update an existing profile or create one if it doesn't exist.
    Profile.objects.update_or_create(user=instance, defaults={})
