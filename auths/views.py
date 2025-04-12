from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.models import auth
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import User

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
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect(reverse("landing:landing_page"))
    
    return render(request, 'auths/login.html', {
            "error": "Invalid Login Credentials"
        })

def logout(request):
    auth.logout(request)
    return redirect("/")

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





