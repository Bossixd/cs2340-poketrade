import django
django.setup()

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import ProfileCards


@login_required(login_url='auths:login')
def hub_view(request):
    if request.GET.get("page"):
        page = request.GET.get("page")
    else:
        return redirect("/pokehub/hub?page=1")
    
    from accounts.models import Profile
    
    try:
        profile = Profile.objects.get(user=request.user)
    except ObjectDoesNotExist:
        profile = Profile.objects.create(user=request.user)
        
    cards = []
    for card in list(ProfileCards.objects.filter(profile=profile)):
        cards.append(card.cards)
    
    context = {
        'user': request.user,
        'profile': profile,
        'cards': cards,
        'page': int(page)
    }
    return render(request, 'pokehub/hub.html', context)