
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from .models import Profile
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
@login_required(login_url='auths:login')
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'profile': Profile.objects.get(user=request.user)
    })

@login_required(login_url='auths:login')
def edit_profile(request):
    if request.method == 'POST':
        # Add profile editing logic here
        return redirect('accounts:profile')
    return render(request, 'accounts/edit_profile.html')

@staff_member_required
def user_list(request):
    users = User.objects.all().select_related('profile')
    profile = Profile.objects.get(user=request.user)
    return render(request, 'accounts/user_list.html', {'users': users, 'profile': profile})

@staff_member_required
def ban_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    profile = Profile.objects.get(user=request.user)
    profile.is_banned = True
    profile.save()
    return redirect('accounts:user_list')

@staff_member_required
def unban_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    profile = Profile.objects.get(user=request.user)
    profile.is_banned = False
    profile.save()
    return redirect('accounts:user_list')

@login_required(login_url='auths:login')
def add_currency(request):
    if request.method == 'POST':
        amount = int(request.POST.get('amount', 100))
        profile = Profile.objects.get(user=request.user)
        profile.currency += amount
        profile.save()
        return redirect('accounts:profile')
    return render(request, 'accounts/add_currency.html')


def logout(request):
    auth_logout(request)
    return redirect('/pokehub/')  # Explicitly redirect to /pokehub/