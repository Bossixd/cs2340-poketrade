# accounts/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Create a profile when a new user is created
    """
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_delete, sender=Profile)
def delete_user_on_profile_deletion(sender, instance, **kwargs):
    """
    Delete the User when their Profile is deleted
    """
    try:
        # Check if the user still exists to avoid errors
        if instance.user and User.objects.filter(pk=instance.user.pk).exists():
            instance.user.delete()
    except User.DoesNotExist:
        # User already deleted
        pass