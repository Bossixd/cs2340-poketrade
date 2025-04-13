import django
django.setup()

from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import ProfileCards, Profile


def hub_view(request):
    if request.GET.get("page"):
        page = request.GET.get("page")
    else:
        return redirect("/pokehub/hub?page=1")

    profile = None
    cards = []

    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            profile = Profile.objects.create(user=request.user)

        for card in list(ProfileCards.objects.filter(profile=profile)):
            cards.append(card.cards)

    context = {
        'user': request.user,
        'profile': profile,
        'cards': cards,
        'page': int(page)
    }
    return render(request, 'pokehub/hub.html', context)