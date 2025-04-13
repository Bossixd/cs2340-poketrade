# accounts/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile, ProfileCards

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    """
    Create a profile when a new user is created
    """
    if created:
        Profile.objects.get_or_create(user=instance)

# Note: We don't need a separate post_delete signal for Profile deletion
# because we're using OneToOneField with CASCADE, which will automatically
# delete the Profile when the User is deleted