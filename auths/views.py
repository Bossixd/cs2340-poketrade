from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import auth
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from django.contrib.auth.models import User
from accounts.models import Profile, ProfileCards
from pokemon.models import Card

import random
import string


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
        email = request.POST.get("email")  # Changed from username to email
        password = request.POST.get("password")

        # First, check if a user with this email exists
        if not User.objects.filter(email=email).exists():
            context["error"] = "Invalid login credentials."
            return render(request, 'auths/login.html', context)

        # Get the username associated with this email
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            context["error"] = "Invalid login credentials."
            return render(request, 'auths/login.html', context)

        # Authenticate using the username (Django auth requires username)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
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

def generate_confirmation_code(length=6):
    """Generate a random confirmation code"""
    return ''.join(random.choices(string.digits, k=length))

def reset(request):
    if request.method == "GET":
        email = request.session.get('reset_email')
        if email:
            return render(request, 'auths/reset_confirm.html', {
                'email': email,
                'code_sent': True
            })
        return render(request, 'auths/reset.html')
    
    elif request.method == "POST":
        # Stage 1: Email submission
        if 'email' in request.POST and 'password' not in request.POST:
            email = request.POST["email"].strip()
            
            if not User.objects.filter(email=email).exists():
                return render(request, 'auths/reset.html', {
                    "error_type": "email",
                    "error": "Email does not exist in our system!"
                })
            
            # Generate and store confirmation code with expiration (5 minutes)
            confirmation_code = generate_confirmation_code()
            request.session['reset_code'] = confirmation_code
            request.session['reset_email'] = email
            request.session['reset_code_attempts'] = 0
            request.session['reset_code_time'] = timezone.now().isoformat()
            
            # Send email with confirmation code
            try:
                send_mail(
                    'Password Reset Confirmation - PokeHub',
                    f'Your password reset confirmation code is: {confirmation_code}\n\n'
                    'This code will expire in 5 minutes. If you didn\'t request this, please ignore this email.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                return render(request, 'auths/reset.html', {
                    "error": "Failed to send confirmation email. Please try again later."
                })
            
            return render(request, 'auths/reset_confirm.html', {
                'email': email,
                'code_sent': True,
                'success': 'A confirmation code has been sent to your email.'
            })
        
        # Stage 2: Code and new password submission
        elif 'confirmation_code' in request.POST and 'password' in request.POST:
            email = request.session.get('reset_email')
            stored_code = request.session.get('reset_code')
            submitted_code = request.POST.get('confirmation_code', '').strip()
            code_time_str = request.session.get('reset_code_time')
            
            # Check if code has expired (5 minutes)
            if code_time_str:
                code_time = timezone.datetime.fromisoformat(code_time_str)
                if timezone.now() - code_time > timedelta(minutes=5):
                    # Clear expired code
                    del request.session['reset_code']
                    del request.session['reset_code_time']
                    return render(request, 'auths/reset_confirm.html', {
                        'email': email,
                        'error': 'Confirmation code has expired. Please request a new one.',
                        'code_sent': False
                    })
            
            # Validate the confirmation code
            if not email or not stored_code or submitted_code != stored_code:
                attempts = request.session.get('reset_code_attempts', 0) + 1
                request.session['reset_code_attempts'] = attempts
                
                if attempts >= 3:
                    # Clear session after too many attempts
                    request.session.pop('reset_code', None)
                    request.session.pop('reset_email', None)
                    request.session.pop('reset_code_attempts', None)
                    request.session.pop('reset_code_time', None)
                    return render(request, 'auths/reset.html', {
                        "error": "Too many failed attempts. Please start over."
                    })
                
                return render(request, 'auths/reset_confirm.html', {
                    'email': email,
                    'error': 'Invalid confirmation code. Please try again.',
                    'code_sent': True
                })
            
            # Validate passwords match
            password = request.POST["password"]
            confirm_password = request.POST.get("confirm_password", "")
            
            if password != confirm_password:
                return render(request, 'auths/reset_confirm.html', {
                    'email': email,
                    'error': "Passwords do not match!",
                    'code_sent': True
                })

            # Validate password strength
            try:
                validate_password(password)
            except Exception as e:
                return render(request, 'auths/reset_confirm.html', {
                    'email': email,
                    'error': "Password is not strong enough! " + str(e),
                    'code_sent': True
                })

            # Update password
            user = User.objects.get(email=email)
            user.set_password(password)
            user.save()
            
            # Clear session data
            request.session.pop('reset_code', None)
            request.session.pop('reset_email', None)
            request.session.pop('reset_code_attempts', None)
            request.session.pop('reset_code_time', None)
            
            # Send confirmation email
            try:
                send_mail(
                    'Password Changed - PokeHub',
                    'Your PokeHub password has been successfully changed.\n\n'
                    'If you didn\'t make this change, please contact support immediately.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                pass  # Password was changed even if email failed
                
            return render(request, 'auths/login.html', {
                'success': 'Your password has been reset successfully. Please login with your new password.'
            })

    return render(request, 'auths/reset.html')


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