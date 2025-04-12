import requests
import json
import pandas as pd

df = pd.read_csv("filtered_pokemons.csv")

names = {}

for index, row in df.iterrows():
    if index % 100 == 0:
        print(index)
    pokedexNumber = int(row['nationalPokedexNumbers'].strip('[]'))
    if pokedexNumber not in names:
        res = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokedexNumber}')
        response = json.loads(res.text)
        names[pokedexNumber] = str(response['name']).capitalize()
        
    df.iloc[index, 0] = names[pokedexNumber]

df.to_csv("cleaned_pokemons.csv", index=False)