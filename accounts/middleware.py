# accounts/middleware.py

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User

from accounts.models import Profile


# accounts/middleware.py
class UserExistenceCheckMiddleware:
    """
    Middleware to ensure authenticated users still exist in the database
    and have valid profiles.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated but doesn't exist in database
        if request.user.is_authenticated:
            try:
                # Try to get the user from the database
                User.objects.get(pk=request.user.pk)

                # Also check if profile exists
                Profile.objects.get(user=request.user)
            except (User.DoesNotExist, Profile.DoesNotExist):
                # User or profile no longer exists in database, logout and redirect
                logout(request)
                return redirect('auths:login')

        response = self.get_response(request)
        return response