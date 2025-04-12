from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

@login_required
def hub_view(request):
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        from accounts.models import Profile
        profile = Profile.objects.create(user=request.user)
    
    context = {
        'user': request.user,
        'profile': profile
    }
    return render(request, 'pokehub/hub.html', context)