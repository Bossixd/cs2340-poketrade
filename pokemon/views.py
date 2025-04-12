from django.shortcuts import render
from .models import Pokemon, Card

# Create your views here.
def list(request):
    cards = Card.objects.filter(pokemon_info__name="Pikachu")
    return render(request, 'pokemon/list.html', {'cards': cards})

def generate(request):
    return render(request, 'pokemon/generate.html')