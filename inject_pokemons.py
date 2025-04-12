import requests
import json
import pandas as pd

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'poketrader.settings')
django.setup()

from pokemon.models import Pokemon, Card

df = pd.read_csv("scraper/cleaned_pokemons.csv")

for index, row in df.iterrows():
    name = row['name']
    hp = float(row['hp'])
    images = json.loads(row['images'].replace("\'", "\""))
    small_image = images['small']
    large_image = images['large']
    types = ", ".join(list(json.loads(row['types'].replace("\'", "\""))))
    nationalPokedexNumbers = int(row['nationalPokedexNumbers'].strip('[]'))
    
    try:
        Pokemon.objects.get(name=name)
    except:
        pokemon = Pokemon(name=name, pokedexNumber=nationalPokedexNumbers)
        pokemon.name = row['name']
        pokemon.save()
    
    pokemon = Pokemon.objects.get(name=name)
    
    card = Card(pokemon_info=pokemon, type=types, hp=hp, small_image=small_image, large_image=large_image)
    card.save()