import os
import discord

from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot("")
bot.load_extension("cogs")
bot.run(TOKEN)