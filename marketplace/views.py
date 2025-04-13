
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def home(request):
    # This is a simple view that renders the marketplace home page.
    return render(request, 'marketplace/home.html')

def roll(request):
    context = {
        'result': 'roll sucessful',
    }
    return render(request, 'marketplace/roll.html', context)

@login_required
def set_desired(request):
    if request.method == "POST":
        desired_card = request.POST.get("desired_card")
        if desired_card:
            request.session["desired_card_id"] = desired_card
    desired_card = request.session.get("desired_card_id", None)
    return render(request, "marketplace/set_desired.html", {"desired_card": desired_card})