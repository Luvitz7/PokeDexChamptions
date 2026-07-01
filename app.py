import discord
from discord.ext import commands
import webserver
import os
from pokeapi import show_pokemon_details, get_pokemon_details, fetch_data

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="$", intents=intents)

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

        embed = discord.Embed(title=show_pokemon["name"].capitalize(), color=discord.Color.blue())
        embed.set_thumbnail(url=show_pokemon["sprites"])
        embed.add_field(name="Height", value=show_pokemon["height"], inline=True)
        embed.add_field(name="Weight", value=show_pokemon["weight"], inline=True)
        embed.add_field(name="Types", value=', '.join([t.capitalize() for t in show_pokemon["types"]]), inline=False)
        embed.add_field(name="Stats", value='\n'.join([f"{stat.capitalize()}: {value}" for stat, value in show_pokemon["stats"].items()]), inline=False)


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

