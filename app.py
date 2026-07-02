import discord
from discord.ext import commands
import webserver
import os
import json
from pokeapi import show_pokemon_details, get_pokemon_details, fetch_data

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

with open("data/moves_es.json", "r", encoding="utf-8") as file:
    moves_es_list = json.load(file)

with open("data/moves_en.json", "r", encoding="utf-8") as file:
    moves_en_list = json.load(file)

with open("data/abilities_en.json", "r", encoding="utf-8") as file:
    abilities_en_list = json.load(file)

with open("data/abilities_es.json", "r", encoding="utf-8") as file:
    abilities_en_list = json.load(file)    

with open("data/dict_es.json", "r", encoding="utf-8") as file:
    ES = json.load(file)  

with open("data/dict_en.json", "r", encoding="utf-8") as file:
    EN = json.load(file)  

MOVES_ES = {
    move["name"].lower(): move
    for move in moves_es_list
}

MOVES_EN = {
    move["name"].lower(): move
    for move in moves_en_list
}

ABILITIES_ES = {
    abilitie["name"].lower(): abilitie
    for abilitie in abilities_en_list
}

ABILITIES_EN = {
    abilitie["name"].lower(): abilitie
    for abilitie in abilities_en_list
}


MAX_LIST_LENGTH = 10  # Maximum number of items to display in the list

STAT_ICONS = {
    "hp": "❤️",
    "attack": "⚔️",
    "defense": "🛡️",
    "special-attack": "✨",
    "special-defense": "🔰",
    "speed": "⚡"
}

TYPE_COLORS = {
    "normal": 0xA8A77A,
    "fire": 0xEE8130,
    "water": 0x6390F0,
    "electric": 0xF7D02C,
    "grass": 0x7AC74C,
    "ice": 0x96D9D6,
    "fighting": 0xC22E28,
    "poison": 0xA33EA1,
    "ground": 0xE2BF65,
    "flying": 0xA98FF3,
    "psychic": 0xF95587,
    "bug": 0xA6B91A,
    "rock": 0xB6A136,
    "ghost": 0x735797,
    "dragon": 0x6F35FC,
    "dark": 0x705746,
    "steel": 0xB7B7CE,
    "fairy": 0xD685AD,
    
    "fuego": 0xEE8130,
    "agua": 0x6390F0,
    "electrico": 0xF7D02C,
    "planta": 0x7AC74C,
    "hielo": 0x96D9D6,
    "lucha": 0xC22E28,
    "veneno": 0xA33EA1,
    "tierra": 0xE2BF65,
    "volador": 0xA98FF3,
    "psíquico": 0xF95587,
    "bicho": 0xA6B91A,
    "roca": 0xB6A136,
    "fantasma": 0x735797,
    "dragon": 0x6F35FC,
    "siniestro": 0x705746,
    "metal": 0xB7B7CE,
    "hada": 0xD685AD
}


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

def format_name(name):
    return name.replace("-", " ").title()

def get_type_color(types):
    if not types:
        return discord.Color.default()
    
    primary_type = types[0].lower()
    color_value = TYPE_COLORS.get(primary_type, 0x000000)
    return discord.Color(color_value)

def find_move(name):
    name = name.lower()

    if move := MOVES_ES.get(name):
        return move, ES

    if move := MOVES_EN.get(name):
        return move, EN

    return None, None

def find_ability(name):
    name = name.lower()

    if move := ABILITIES_ES.get(name):
        return move, ES

    if move := ABILITIES_EN.get(name):
        return move, EN

    return None, None

@bot.command()
async def poke(ctx, *arg):
    if not arg:
        await ctx.send("Please provide a Pokémon name or ID.")
        return

    name_pokemon = ' '.join(arg).lower()
    url = f"https://pokeapi.co/api/v2/pokemon/{name_pokemon}"

    data = fetch_data(url)

    if data:
        pokemon, stats_poke_champions, moves_pokemon = get_pokemon_details(data)
        show_pokemon = show_pokemon_details(pokemon, stats_poke_champions)

        embed = discord.Embed(title=format_name(show_pokemon["name"]), color=get_type_color(show_pokemon["types"]))
        embed.set_thumbnail(url=show_pokemon["sprites"])
        embed.add_field(name=ES["characteristics"]["height"], value=(f"{show_pokemon['height']}m"), inline=True)
        embed.add_field(name=ES["characteristics"]["weight"], value=(f"{show_pokemon['weight']}kg"), inline=True)
        embed.add_field(name=ES["characteristics"]["abilities"], value='\n'.join(format_name(ability) for ability in pokemon["abilities"]), inline=False)
        embed.add_field(name=ES["characteristics"]["types"], value=', '.join(format_name(t) for t in show_pokemon["types"]), inline=False)
        bst = sum(stats_poke_champions.values())
        embed.add_field(name=ES["characteristics"]["bst"], value=(f"📊 BST: {bst}"), inline=False)
        embed.add_field(name=ES["characteristics"]["stats"], value='\n'.join([f"{STAT_ICONS.get(stat, '')} {format_name(ES["stats"][stat])}: {value}" for stat, value in show_pokemon["stats"].items()]), inline=False)

        await ctx.send(embed=embed)

    else:
        await ctx.send(f"No se encontró información para el Pokémon '{' '.join(arg)}'. Por favor, verifica el nombre o ID e inténtalo de nuevo.")

@bot.command()
async def poke_move(ctx, *args):
    if not args:
        await ctx.send("Menciona el nombre del movimiento.")
        return
        
    move_info, dictionary = find_move(' '.join(args))

    if move_info:
        embed = discord.Embed(title=format_name(move_info["name"]), color=get_type_color([move_info["type"]]))
        embed.add_field(name=dictionary["characteristics"]["types"], value=format_name(move_info["type"]), inline=True)
        embed.add_field(name=dictionary["characteristics"]["category"], value=format_name(move_info["category"]), inline=True)
        embed.add_field(name=dictionary["characteristics"]["power"], value=move_info["power"], inline=True)
        embed.add_field(name=dictionary["characteristics"]["usage"], value=move_info["usage"], inline=True)
        embed.add_field(name=dictionary["characteristics"]["accuracy"], value=move_info["accuracy"], inline=True)
        embed.add_field(name="PP", value=move_info["pp"], inline=True)
        embed.add_field(name=dictionary["characteristics"]["effect"], value=move_info["effect"], inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No se encontró información para el movimiento '{' '.join(args)}'. Por favor, verifica el nombre e inténtalo de nuevo.")

@bot.command()
async def poke_ability(ctx, *args):
    if not args:
        await ctx.send("Menciona el nombre de la habilidad.")
        return
        
    ability_info, dictionary = find_ability(' '.join(args))
    
    if ability_info:
        embed = discord.Embed(title=format_name(ability_info["name"]), color=discord.Color.blue())
        embed.add_field(name=dictionary["characteristics"]["effect"], value=ability_info["effect"], inline=False)
        embed.add_field(name=dictionary["characteristics"]["poke_ability"], value='\n'.join(format_name(" • "+ pokemon) for pokemon in ability_info["pokemons"][:MAX_LIST_LENGTH]), inline=False)
        if len(ability_info["pokemons"]) > MAX_LIST_LENGTH:
            embed.add_field(name="And more...", value=f"{dictionary["characteristics"]["poke_ability"], " ", len(ability_info['pokemons'])}", inline=False)

        await ctx.send(embed=embed)
    else:
        await ctx.send(f"No se encontró información para la habilidad '{' '.join(args)}'. Por favor, verifica el nombre e inténtalo de nuevo.")

@bot.command()
async def poke_help(ctx):
    embed = discord.Embed(title="Ayuda del Bot de Pokémon", color=discord.Color.green())
    embed.add_field(name="$poke <nombre o ID del Pokémon>", value="Muestra información sobre el Pokémon especificado.", inline=False)
    embed.add_field(name="$poke_help", value="Muestra esta ayuda.", inline=False)
    embed.add_field(name="$poke_move <nombre del movimiento>", value="Muestra información sobre el movimiento especificado.", inline=False)
    embed.add_field(name="$poke_ability <nombre de la habilidad>", value="Muestra información sobre la habilidad especificada.", inline=False)
    embed.add_field(name="Mega Evoluciones", value="Para buscar una megaevolución, utiliza el nombre completo, por ejemplo: $poke sceptile-mega", inline=False)


    await ctx.send(embed=embed)

webserver.keep_alive()
bot.run(DISCORD_TOKEN)

