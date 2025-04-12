import requests
import json

import pandas as pd

keys = ['name', 'id', 'hp', 'number', 'set', 'artist', 'images', 'types', 'nationalPokedexNumbers']

df = pd.DataFrame(columns=keys)

page_number = 1
cards = 0
while cards < 18876:
    res = requests.get(f'https://api.pokemontcg.io/v2/cards?page={page_number}',
                        headers={
                            'X-Api-Key': '127c4de8-3d66-4d0d-a67e-bec50bbccb36'
                        })
    response = json.loads(res.text)
    with open('test.json', 'w') as outfile:
        json.dump(response, outfile)
        
    print("page_number: ", page_number)
    
    with open('test.json') as json_file:
        data = json.load(json_file)
        
        arr = []
        for i in range(len(data['data'])):
            arrr = []
            for key in keys:
                try:
                    arrr.append(data['data'][i][key])
                except:
                    arrr.append(None)
            arr.append(arrr)
        
        df = pd.concat([df, pd.DataFrame(arr, columns=keys)])
        df.to_csv('pokemons.csv', index=False)
    
    cards += 250
    page_number += 1