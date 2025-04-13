from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

from django.contrib.auth.models import auth
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import User
from accounts.models import Profile, ProfileCards
from pokemon.models import Card

import random


def register(request):
    if request.method == "GET":
        return render(request, 'auths/register.html', {})
    elif request.method == "POST":
        if User.objects.filter(username=request.POST["username"]).exists():
            return render(request, 'auths/register.html', {
                "error_type": "username",
                "error": "Username already exists!"
            })

        try:
            validate_email(request.POST["email"])
        except:
            return render(request, 'auths/register.html', {
                "error_type": "email",
                "error": "Email is not valid!"
            })

        if User.objects.filter(email=request.POST["email"]).exists():
            return render(request, 'auths/register.html', {
                "error_type": "email",
                "error": "Email already exists!"
            })

        try:
            validate_password(request.POST["password"])
        except:
            return render(request, 'auths/register.html', {
                "error_type": "password",
                "error": "Password is not strong enough!"
            })

        # Create the user
        user = User(username=request.POST["username"], email=request.POST["email"],
                    password=make_password(request.POST["password"]))
        user.save()

        # Get the user's profile (created via signal)
        profile = Profile.objects.get(user=user)

        # Define starter Pokémon names
        starter_names = ['Bulbasaur', 'Charmander', 'Squirtle', 'Pikachu',
                         'Chikorita', 'Cyndaquil', 'Totodile',
                         'Treecko', 'Torchic', 'Mudkip',
                         'Turtwig', 'Chimchar', 'Piplup',
                         'Snivy', 'Tepig', 'Oshawott']

        # Try to find cards for starter Pokémon
        starter_cards = Card.objects.filter(pokemon_info__name__in=starter_names)

        # If no specific starter cards exist, fall back to any cards
        if not starter_cards.exists():
            starter_cards = Card.objects.all()

        if starter_cards.exists():
            # Select a random starter card
            random_card = random.choice(list(starter_cards))

            # Link the card to the user's profile
            ProfileCards.objects.create(profile=profile, cards=random_card)

            # Redirect with starter_card parameter and the card name
            card_name = random_card.pokemon_info.name
            return HttpResponseRedirect(reverse("auths:login") + f"?starter_card=true&card_name={card_name}")

        return HttpResponseRedirect(reverse("auths:login"))


def login(request):
    # Check if the user was redirected from registration
    starter_card = request.GET.get('starter_card', None)
    card_name = request.GET.get('card_name', None)

    context = {
        'starter_card': starter_card,
        'card_name': card_name
    }

    if request.method == "GET":
        return render(request, 'auths/login.html', context)
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # First, check if the user exists in the database
        if not User.objects.filter(username=username).exists():
            context["error"] = "Invalid login credentials."
            return render(request, 'auths/login.html', context)

        # If the user exists, then try to authenticate
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Try to get the profile, create one if it doesn't exist
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                # Create a new profile for this user
                profile = Profile.objects.create(user=user)

            if profile.is_banned:
                context["error"] = "Your account has been banned. Please contact support."
                return render(request, 'auths/login.html', context)

            auth_login(request, user)
            return redirect("landing:landing_page")

        context["error"] = "Invalid login credentials."
        return render(request, 'auths/login.html', context)


def logout(request):
    auth_logout(request)
    # Redirect to hub page instead of homepage
    return redirect("/pokehub/hub?page=1")


def reset(request):
    if request.method == "GET":
        return render(request, 'auths/reset.html')
    elif request.method == "POST":

        if not User.objects.filter(email=request.POST["email"]).exists():
            return render(request, 'auths/reset.html', {
                "error_type": "email",
                "error": "Email does not exist!"
            })

        if request.POST["password"] != request.POST["confirm_password"]:
            return render(request, 'auths/reset.html', {
                "error_type": "password",
                "error": "Passwords do not match!"
            })

        try:
            validate_password(request.POST["password"])
        except:
            return render(request, 'auths/reset.html', {
                "error_type": "password",
                "error": "Password is not strong enough!"
            })

        User.objects.filter(email=request.POST["email"]).update(password=make_password(request.POST["password"]))

        return render(request, 'auths/login.html')


def admin_login(request):
    error = None
    if request.method == 'POST':
        # Retrieve credentials from form submission.
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate the user.
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if the user is an admin.
            if user.is_staff or user.is_superuser:
                auth_login(request, user)  # Call the aliased login function.
                # Redirect to the desired page.
                return redirect('pokemon:generate_create')  # Use URL name if possible.
            else:
                error = "Not an admin"
        else:
            error = "Invalid credentials"
    return render(request, 'pokemon/generate.html', {'error': error})