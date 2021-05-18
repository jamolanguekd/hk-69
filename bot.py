import os
import discord

from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot("")
cogs = ["maincog","polls","responses"]
for cog in cogs:
    bot.load_extension(f"cogs.{cog}")
bot.run(TOKEN)