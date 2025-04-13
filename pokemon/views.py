from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.db.models import Q
from accounts.models import ProfileCards, Profile
from .models import Card
import re


from auths.views import login

from django.shortcuts import render
from .models import Pokemon, Card

import os
from dotenv import load_dotenv
import requests

load_dotenv()
OPENAPI_KEY = os.getenv("OPENAPI_KEY")

# Create your views here.
def list(request):
    print(request.GET)
    query = request.GET.get("q") or ''
    page = request.GET.get("page") or ''
    cards = Card.objects.all()
    
    print(query, page)
    
    if page == '':
        return redirect(f'/pokemon/list?q={query}&page=1')
    
    try:
        page = int(page)
        if page < 1:
            page = 1
    except:
        return redirect(f'/pokemon/list?q={query}&page=1')

    if query:
        filters = Q()

        if query == "$$$all":
            Card.objects.all()
        elif query:
            filters = (
                    Q(pokemon_info__name__icontains=query) |
                    Q(type__icontains=query)

            )

            if query.isdigit():
                filters |= Q(id=int(query)) | Q(hp=int(query))

        cards = Card.objects.filter(filters).distinct()
    
    if 20 * (page - 1) > cards.count():
        page -= 1
    
    cards = cards[20 * (page - 1) : 20 * page]
    

    context = {'cards': cards, 'query': query, 'page': page}

    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            profile = None
        context['profile'] = profile

    return render(request, 'pokemon/list.html', context)


@login_required(login_url='auths:login')
def generate(request):
    user = request.user
    if user is not None:
        # Check if the user is an admin. You can change this to your preferred flag.
        print(user.is_staff)
        if not user.is_staff:
            return redirect('/landing')
    else:
        print("redirect")
        return redirect('/landing')
        
    if request.method == "GET":
        return render(request, 'pokemon/generate.html')
    elif request.method == "POST":
        
        name = request.POST.get('name')
        type = request.POST.get('type')
        secondary_type = request.POST.get('secondary-type')
        hp = request.POST.get('hp')
        shiny = request.POST.get('shiny')
        legendary = request.POST.get('legendary')
        mega = request.POST.get('mega')
        description = request.POST.get('description')
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAPI_KEY}',
        }
        
        prompt = f"One Pokemon Card Only and nothing else. Name: {name}. {type} {secondary_type if secondary_type else ''} {hp} health points. {'Shiny' if shiny else ''} {'Legendary' if legendary else ''} {'Mega' if mega else ''}. {description}"

        json_data = {
            'prompt': prompt,
            'n': 1,
            'size': '1024x1792',
            'model': 'dall-e-3',
        }

        response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, json=json_data)
        
        url = response.json()['data'][0]['url']

        pokemon = Pokemon(name=name)
        pokemon.save()
        
        card = Card(pokemon_info=pokemon, type=f"{type}, {secondary_type}", hp=hp, small_image=url, large_image=url)
        card.save()
        context = {
            'name': name,
            'type': type.lower(),
            'secondary_type': secondary_type.lower(),
            'hp': hp,
            'image_url': url
        }

        return render(request, 'pokemon/card.html', context=context)


def card(request):
    full_url = request.get_full_path()
    id = request.GET.get('id')
    from_param = request.GET.get('from', 'list')  # Default to list if not specified
    query = request.GET.get('q', '')  # Get the search query if available
    page = request.GET.get('page', '1')  # Get the current page if available

    card = Card.objects.get(id=id)

    context = {
        'name': card.pokemon_info.name,
        'type': card.type.split(",")[0].lower(),
        'secondary_type': card.type.split(",")[1].lower() if len(card.type.split(",")) > 1 else None,
        'hp': card.hp,
        'image_url': card.large_image,
        'from': from_param,  # Pass the 'from' parameter to the template
        'query': query,  # Pass the search query
        'page': page  # Pass the current page
    }
    return render(request, 'pokemon/card.html', context=context)


@staff_member_required
def create_starter_cards(request):
    """
    Admin-only view to create starter Pokémon cards if they don't exist.
    This ensures there are proper starter cards to give to new users.
    """
    # Define starter Pokémon with their types and HP values
    starter_data = [
        {'name': 'Bulbasaur', 'type': 'grass', 'hp': 45,
         'small_image': '/static/pokemon/starters/bulbasaur_small.jpg',
         'large_image': '/static/pokemon/starters/bulbasaur_large.jpg'},
        {'name': 'Charmander', 'type': 'fire', 'hp': 39,
         'small_image': '/static/pokemon/starters/charmander_small.jpg',
         'large_image': '/static/pokemon/starters/charmander_large.jpg'},
        {'name': 'Squirtle', 'type': 'water', 'hp': 44,
         'small_image': '/static/pokemon/starters/squirtle_small.jpg',
         'large_image': '/static/pokemon/starters/squirtle_large.jpg'},
        {'name': 'Pikachu', 'type': 'electric', 'hp': 35,
         'small_image': '/static/pokemon/starters/pikachu_small.jpg',
         'large_image': '/static/pokemon/starters/pikachu_large.jpg'},
    ]

    created_count = 0

    # Create each starter Pokémon if it doesn't exist
    for data in starter_data:
        # Check if this Pokémon already exists
        pokemon, created = Pokemon.objects.get_or_create(
            name=data['name'],
            defaults={'pokedexNumber': 0}  # This would normally be set to the proper Pokédex number
        )

        # Check if a card exists for this Pokémon
        if not Card.objects.filter(pokemon_info=pokemon).exists():
            Card.objects.create(
                pokemon_info=pokemon,
                type=data['type'],
                hp=data['hp'],
                small_image=data['small_image'],
                large_image=data['large_image']
            )
            created_count += 1

    return HttpResponse(f'Created {created_count} new starter Pokémon cards')

import re

def extract_card_id_from_url(url):
    pattern = r'\?id=([^&]+)&from'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return ''
