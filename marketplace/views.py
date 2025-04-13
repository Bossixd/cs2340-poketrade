
from django.shortcuts import render

def home(request):
    # This is a simple view that renders the marketplace home page.
    return render(request, 'marketplace/home.html')

def roll(request):
    context = {
        'result': 'roll sucessful',
    }
    return render(request, 'marketplace/roll.html', context)
