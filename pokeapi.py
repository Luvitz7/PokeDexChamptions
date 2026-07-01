import requests
from pprint import pprint

# name_pokemon = input("Ingresa el nombre del Pokemon o su numero de pokedex: ").lower()

url= f"https://pokeapi.co/api/v2/pokemon/dragonite"

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json()  # Assuming the response is in JSON format
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

data = fetch_data(url)

def get_pokemon_details(data):
    if data:
        pokemon = {
            "name": data.get("name"),
            "id": data.get("id"),
            "height": data.get("height"),
            "weight": data.get("weight"),
            "types": [t["type"]["name"] for t in data.get("types", [])],
            "stats": {stat["stat"]["name"]: stat["base_stat"] for stat in data.get("stats", [])},
            "sprites": data.get("sprites", {}).get("front_default"),
            "abilities": [ability["ability"]["name"] for ability in data.get("abilities", [])],
        }

        stats_poke_champions = {
            "hp": pokemon["stats"].get("hp")+75,
            "attack": pokemon["stats"].get("attack")+20,
            "defense": pokemon["stats"].get("defense")+20,
            "special-attack": pokemon["stats"].get("special-attack")+20,
            "special-defense": pokemon["stats"].get("special-defense")+20,
            "speed": pokemon["stats"].get("speed")+20,
        }

        moves_pokemon = [move["move"]["name"] for move in data.get("moves", [])]

    return pokemon, stats_poke_champions, moves_pokemon

def show_pokemon_details(pokemon, stats_poke_champions):
    
    show_pokemon = {
        "sprites": pokemon["sprites"],
        "name": pokemon["name"],
        "height": pokemon["height"],
        "weight": pokemon["weight"],
        "types": pokemon["types"],
        "stats": stats_poke_champions,
        }

    return show_pokemon



