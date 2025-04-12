import requests
import json
import pandas as pd

df = pd.read_csv("cleaned_pokemons.csv")

print(df.where(df['name'].str.contains('-')).dropna()['name'].unique())