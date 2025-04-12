from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from auths.views import login
from .models import Pokemon, Card

import os
from dotenv import load_dotenv
import requests

load_dotenv()
OPENAPI_KEY = os.getenv("OPENAPI_KEY")

# Create your views here.
def list(request):
    cards = Card.objects.filter(pokemon_info__name="Pikachu")
    return render(request, 'pokemon/list.html', {'cards': cards})

def generate(request):
    """
    This view handles the login form.
    It should be mapped to the URL /pokemon/generate.
    """
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if the user is an admin. You can change this to your preferred flag.
            if user.is_staff:
                auth_login(request, user)
                # Redirect admin users to the create page.
                return redirect('pokemon:generate_create')
            else:
                error = "You are not authorized to access this page."
        else:
            error = "Invalid credentials. Please try again."
    return render(request, 'pokemon/generate.html', {'error': error})


@login_required(login_url='pokemon:generate')
def generate_create(request):
    """
    This view handles the creation functionality.
    It is only accessible by logged-in users.
    Additional check: if the user is not an admin, you can also choose
    to either show an error or redirect them.
    """
    if not request.user.is_staff:
        # Optionally, you can add a message informing the user or simply redirect.
        return redirect('pokemon:generate')

    # Your logic for generating/creating Pokemon would go here.
    return render(request, 'pokemon/create.html')