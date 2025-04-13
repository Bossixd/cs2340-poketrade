# Create this file as 'accounts/auth_backends.py'

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class ExistenceCheckingModelBackend(ModelBackend):
    """
    A custom authentication backend that checks if users exist before authenticating.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # First check if the user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        # Then proceed with normal authentication
        return super().authenticate(request, username=username, password=password, **kwargs)