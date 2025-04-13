# accounts/middleware.py

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.models import User


class UserExistenceCheckMiddleware:
    """
    Middleware to ensure authenticated users still exist in the database.
    This handles cases where a user is deleted but their session remains active.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated but doesn't exist in database
        if request.user.is_authenticated:
            try:
                # Try to get the user from the database
                User.objects.get(pk=request.user.pk)
            except User.DoesNotExist:
                # User no longer exists in database, logout and redirect
                logout(request)
                return redirect('auths:login')

        response = self.get_response(request)
        return response