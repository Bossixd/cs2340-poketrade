from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout

from django.contrib.auth.models import auth
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import User
from accounts.models import Profile

# Create your views here.
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

        user = User(username=request.POST["username"], email=request.POST["email"], password=make_password(request.POST["password"]))
        user.save()
        return HttpResponseRedirect(reverse("auths:login"))

def login(request):
    if request.method == "GET":
        return render(request, 'auths/login.html')
    elif request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            profile = Profile.objects.get(user=user)
            if profile.is_banned:
                return render(request, 'auths/login.html', {
                    "error": "Your account has been banned. Please contact support."
                })
            auth_login(request, user)
            return redirect("landing:landing_page")
    return render(request, 'auths/login.html', {
        "error": "Invalid login credentials."
    })

def logout(request):
    auth.logout(request)
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
            return render(request, 'auths/register.html', {
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
