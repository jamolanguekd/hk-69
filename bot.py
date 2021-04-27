import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    curseVocab = ["TANGINA","GAGO","PAKYU"]
    response = ""
    for word in curseVocab:
        if message.content.upper().find(word) != -1:
            response += (word.lower() + " ")
    if response != "":
        response = f"{response}ka rin {message.author.mention}!!"
        await message.channel.send(response)

client.run(TOKEN)