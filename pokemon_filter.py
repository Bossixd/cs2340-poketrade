import pandas as pd

df = pd.read_csv("pokemons.csv")

pokemons = df.where((df['nationalPokedexNumbers'] != None) & (~(df['nationalPokedexNumbers'].str.contains(',', na=False)))).dropna()

pokemons[['name', 'id', 'hp', 'number', 'images', 'types', 'nationalPokedexNumbers']].to_csv("filtered_pokemons.csv", index=False)