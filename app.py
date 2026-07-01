import discord
from discord.ext import commands
import webserver
import os
from pokeapi import show_pokemon_details, get_pokemon_details, fetch_data

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

def format_name(name):
    return name.replace("-", " ").title()

STAT_ICONS = {
    "hp": "❤️",
    "attack": "⚔️",
    "defense": "🛡️",
    "special-attack": "✨",
    "special-defense": "🔰",
    "speed": "⚡"
}

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


        embed = discord.Embed(title=format_name(show_pokemon["name"]), color=discord.Color.blue())
        embed.set_thumbnail(url=show_pokemon["sprites"])
        embed.add_field(name="Height", value=(f"{show_pokemon['height']}m"), inline=True)
        embed.add_field(name="Weight", value=(f"{show_pokemon['weight']}kg"), inline=True)
        embed.add_field(name="Abilities", value='\n'.join(format_name(ability) for ability in pokemon["abilities"]), inline=False)
        embed.add_field(name="Types", value=', '.join(format_name(t) for t in show_pokemon["types"]), inline=False)
        bst = sum(stats_poke_champions.values())
        embed.add_field(name="Base Stat Total", value=(f"📊 BST: {bst}"), inline=False)
        embed.add_field(name="Stats", value='\n'.join([f"{STAT_ICONS.get(stat, '')} {format_name(stat)}: {value}" for stat, value in show_pokemon["stats"].items()]), inline=False)

        await ctx.send(embed=embed)

    else:
        await ctx.send(f"No se encontró información para el Pokémon '{' '.join(arg)}'. Por favor, verifica el nombre o ID e inténtalo de nuevo.")

@bot.command()
async def poke_help(ctx):
    embed = discord.Embed(title="Ayuda del Bot de Pokémon", color=discord.Color.green())
    embed.add_field(name="$poke <nombre o ID del Pokémon>", value="Muestra información sobre el Pokémon especificado.", inline=False)
    embed.add_field(name="$poke_help", value="Muestra esta ayuda.", inline=False)
    embed.add_field(name="Mega Evoluciones", value="Para buscar una megaevolución, utiliza el nombre completo, por ejemplo: $poke sceptile-mega", inline=False)

    await ctx.send(embed=embed)

webserver.keep_alive()
bot.run(DISCORD_TOKEN)

