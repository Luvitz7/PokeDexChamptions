import json
import os

import discord
from discord.ext import commands

import webserver
from pokeapi import fetch_data, get_pokemon_details, show_pokemon_details
from pokemon_resolver import resolve_pokemon_query
from search import build_search_index, search_with_suggestions

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

with open("data/moves_es.json", "r", encoding="utf-8") as file:
    moves_es_list = json.load(file)

with open("data/moves_en.json", "r", encoding="utf-8") as file:
    moves_en_list = json.load(file)

with open("data/abilities_en.json", "r", encoding="utf-8") as file:
    abilities_en_list = json.load(file)

with open("data/abilities_es.json", "r", encoding="utf-8") as file:
    abilities_es_list = json.load(file)

with open("data/dict_es.json", "r", encoding="utf-8") as file:
    ES = json.load(file)

with open("data/dict_en.json", "r", encoding="utf-8") as file:
    EN = json.load(file)

MOVES_SEARCH_ES = build_search_index(moves_es_list)
MOVES_SEARCH_EN = build_search_index(moves_en_list)
ABILITIES_SEARCH_ES = build_search_index(abilities_es_list)
ABILITIES_SEARCH_EN = build_search_index(abilities_en_list)

MAX_LIST_LENGTH = 10

STAT_ICONS = {
    "hp": "❤️",
    "attack": "⚔️",
    "defense": "🛡️",
    "special-attack": "✨",
    "special-defense": "🔰",
    "speed": "⚡",
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
    "psiquico": 0xF95587,
    "bicho": 0xA6B91A,
    "roca": 0xB6A136,
    "fantasma": 0x735797,
    "siniestro": 0x705746,
    "metal": 0xB7B7CE,
    "hada": 0xD685AD,
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
    return discord.Color(TYPE_COLORS.get(primary_type, 0x000000))


def find_move(name):
    move, dictionary, suggestions = search_with_suggestions(
        name,
        [
            (*MOVES_SEARCH_ES, {"language": "es", "dictionary": ES}),
            (*MOVES_SEARCH_EN, {"language": "en", "dictionary": EN}),
        ],
    )

    if move:
        return move, dictionary, []

    return None, None, suggestions


def find_ability(name):
    ability, dictionary, suggestions = search_with_suggestions(
        name,
        [
            (*ABILITIES_SEARCH_ES, {"language": "es", "dictionary": ES}),
            (*ABILITIES_SEARCH_EN, {"language": "en", "dictionary": EN}),
        ],
    )

    if ability:
        return ability, dictionary, []

    return None, None, suggestions


def build_move_embed(move_info, dictionary):
    embed = discord.Embed(
        title=format_name(move_info["name"]),
        color=get_type_color([move_info["type"]]),
    )
    embed.add_field(name=dictionary["characteristics"]["types"], value=format_name(move_info["type"]), inline=True)
    embed.add_field(name=dictionary["characteristics"]["category"], value=format_name(move_info["category"]), inline=True)
    embed.add_field(name=dictionary["characteristics"]["power"], value=move_info["power"], inline=True)
    embed.add_field(name=dictionary["characteristics"]["usage"], value=move_info["usage"], inline=True)
    embed.add_field(name=dictionary["characteristics"]["accuracy"], value=move_info["accuracy"], inline=True)
    embed.add_field(name="PP", value=move_info["pp"], inline=True)
    embed.add_field(name=dictionary["characteristics"]["effect"], value=move_info["effect"], inline=False)
    return embed


def build_ability_embed(ability_info, dictionary):
    embed = discord.Embed(title=format_name(ability_info["name"]), color=discord.Color.blue())
    embed.add_field(name=dictionary["characteristics"]["effect"], value=ability_info["effect"], inline=False)
    embed.add_field(
        name=dictionary["characteristics"]["poke_ability"],
        value="\n".join(f"- {format_name(pokemon)}" for pokemon in ability_info["pokemons"][:MAX_LIST_LENGTH]),
        inline=False,
    )
    if len(ability_info["pokemons"]) > MAX_LIST_LENGTH:
        embed.add_field(
            name="And more...",
            value=f"{dictionary['characteristics']['poke_ability']} + {len(ability_info['pokemons']) - MAX_LIST_LENGTH} more",
            inline=False,
        )
    return embed


def build_pokemon_embed(data):
    pokemon, stats_poke_champions, _moves_pokemon = get_pokemon_details(data)
    show_pokemon = show_pokemon_details(pokemon, stats_poke_champions)

    embed = discord.Embed(title=format_name(show_pokemon["name"]), color=get_type_color(show_pokemon["types"]))
    embed.set_thumbnail(url=show_pokemon["sprites"])
    embed.add_field(name=ES["characteristics"]["height"], value=f"{show_pokemon['height']}m", inline=True)
    embed.add_field(name=ES["characteristics"]["weight"], value=f"{show_pokemon['weight']}kg", inline=True)
    embed.add_field(
        name=ES["characteristics"]["abilities"],
        value="\n".join(format_name(ability) for ability in pokemon["abilities"]),
        inline=False,
    )
    embed.add_field(
        name=ES["characteristics"]["types"],
        value=", ".join(format_name(t) for t in show_pokemon["types"]),
        inline=False,
    )
    bst = sum(stats_poke_champions.values())
    embed.add_field(name=ES["characteristics"]["bst"], value=f"📊 BST: {bst}", inline=False)
    embed.add_field(
        name=ES["characteristics"]["stats"],
        value="\n".join(
            f"{STAT_ICONS.get(stat, '')} {format_name(ES['stats'][stat])}: {value}"
            for stat, value in show_pokemon["stats"].items()
        ),
        inline=False,
    )
    return embed


class SuggestionButton(discord.ui.Button):
    def __init__(self, label, target_name, kind):
        super().__init__(label=label[:80], style=discord.ButtonStyle.secondary)
        self.target_name = target_name
        self.kind = kind

    async def callback(self, interaction: discord.Interaction):
        if self.kind == "move":
            move_info, dictionary, _ = find_move(self.target_name)
            if move_info:
                await interaction.response.edit_message(
                    content=None,
                    embed=build_move_embed(move_info, dictionary),
                    view=None,
                )
                return

        if self.kind == "ability":
            ability_info, dictionary, _ = find_ability(self.target_name)
            if ability_info:
                await interaction.response.edit_message(
                    content=None,
                    embed=build_ability_embed(ability_info, dictionary),
                    view=None,
                )
                return

        if self.kind == "pokemon":
            data = fetch_data(f"https://pokeapi.co/api/v2/pokemon/{self.target_name}")
            if data:
                await interaction.response.edit_message(
                    content=None,
                    embed=build_pokemon_embed(data),
                    view=None,
                )
                return

        await interaction.response.send_message("No pude resolver esa sugerencia.", ephemeral=True)


class SuggestionView(discord.ui.View):
    def __init__(self, suggestions, kind):
        super().__init__(timeout=60)
        for item in suggestions:
            if kind in {"move", "ability"}:
                label = item[0]["name"]
                target = item[0]["name"]
            else:
                label = item
                target = item

            self.add_item(SuggestionButton(label, target, kind))


@bot.command()
async def poke(ctx, *arg):
    if not arg:
        await ctx.send("Please provide a Pokemon name or ID.")
        return

    query = " ".join(arg)
    pokemon_slug, suggestions = resolve_pokemon_query(query)

    if pokemon_slug:
        data = fetch_data(f"https://pokeapi.co/api/v2/pokemon/{pokemon_slug}")
        if data:
            await ctx.send(embed=build_pokemon_embed(data))
            return

    if suggestions:
        await ctx.send(
            content=f"No encontré exactamente '{query}'. Quizá quisiste decir:",
            view=SuggestionView(suggestions, "pokemon"),
        )
    else:
        await ctx.send(
            f"No se encontró información para el Pokemon '{query}'. Por favor, verifica el nombre o ID e inténtalo de nuevo."
        )


@bot.command()
async def poke_move(ctx, *args):
    if not args:
        await ctx.send("Menciona el nombre del movimiento.")
        return

    move_info, dictionary, suggestions = find_move(" ".join(args))

    if move_info:
        await ctx.send(embed=build_move_embed(move_info, dictionary))
    elif suggestions:
        await ctx.send(
            content=f"No encontré exactamente '{' '.join(args)}'. Quizá quisiste decir:",
            view=SuggestionView(suggestions, "move"),
        )
    else:
        await ctx.send(
            f"No se encontró información para el movimiento '{' '.join(args)}'. Por favor, verifica el nombre e inténtalo de nuevo."
        )


@bot.command()
async def poke_ability(ctx, *args):
    if not args:
        await ctx.send("Menciona el nombre de la habilidad.")
        return

    ability_info, dictionary, suggestions = find_ability(" ".join(args))

    if ability_info:
        await ctx.send(embed=build_ability_embed(ability_info, dictionary))
    elif suggestions:
        await ctx.send(
            content=f"No encontré exactamente '{' '.join(args)}'. Quizá quisiste decir:",
            view=SuggestionView(suggestions, "ability"),
        )
    else:
        await ctx.send(
            f"No se encontró información para la habilidad '{' '.join(args)}'. Por favor, verifica el nombre e inténtalo de nuevo."
        )


@bot.command()
async def poke_help(ctx):
    embed = discord.Embed(title="Ayuda del Bot de Pokemon", color=discord.Color.green())
    embed.add_field(
        name="$poke <nombre o ID del Pokemon>",
        value="Muestra información sobre el Pokemon especificado.",
        inline=False,
    )
    embed.add_field(name="$poke_help", value="Muestra esta ayuda.", inline=False)
    embed.add_field(
        name="$poke_move <nombre del movimiento>",
        value="Muestra información sobre el movimiento especificado.",
        inline=False,
    )
    embed.add_field(
        name="$poke_ability <nombre de la habilidad>",
        value="Muestra información sobre la habilidad especificada.",
        inline=False,
    )
    embed.add_field(
        name="Mega Evoluciones",
        value="Para buscar una megaevolución, utiliza el nombre completo, por ejemplo: $poke sceptile-mega",
        inline=False,
    )

    await ctx.send(embed=embed)


webserver.keep_alive()
bot.run(DISCORD_TOKEN)
