from django.shortcuts import render

# Create your views here.
# accounts/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User

@staff_member_required
def user_list(request):
    """
    List all regular users for management.
    (You can filter out admins if desired.)
    """
    users = User.objects.filter(is_staff=False)
    return render(request, 'accounts/user_list.html', {'users': users})

@staff_member_required
def ban_user(request, user_id):
    """
    Bans a user by setting their profile's is_banned to True.
    """
    user = get_object_or_404(User, pk=user_id)
    if not user.is_staff:
        user.profile.is_banned = True
        user.profile.save()
    return redirect('accounts:user_list')

@staff_member_required
def unban_user(request, user_id):
    """
    Unbans a user by setting their profile's is_banned to False.
    """
    user = get_object_or_404(User, pk=user_id)
    if not user.is_staff:
        user.profile.is_banned = False
        user.profile.save()
    return redirect('accounts:user_list')