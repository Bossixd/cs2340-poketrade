from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Card


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
    id = request.GET['id']
    card = Card.objects.get(id=id)
    
    context = {
        'name': card.pokemon_info.name,
        'type': card.type.split(",")[0].lower(),
        'secondary_type': card.type.split(",")[1].lower() if len(card.type.split(",")) > 1 else None,
        'hp': card.hp,
        'image_url': card.large_image
    }
    return render(request, 'pokemon/card.html', context=context)