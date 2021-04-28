import os
import discord

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    # TODO: Put in another function
    # MURA RESPONDER
    curseVocab = ["TANGINA","GAGO","PAKYU","BWISET"]
    response = ""
    for word in curseVocab:
        if message.content.upper().find(word) != -1:
            print(f"Detected curse word from {message.author}")
            response += (word.lower() + " ")
    if response != "":
        response = f"{response}ka rin {message.author.mention}!!"
        await message.channel.send(response)
        
    
    # NP BRO RESPONDER
    thanksVocab = ["THANKS", "THANK YOU", "SALAMAT", "LAMAT", "TY"]

    for word in thanksVocab:
        if message.content.upper().find(word) != -1 and message.content.find(client.user.id) != -1:
            print(f"Detected thanks from {message.author}")
            response = f"np bro {message.author.mention}"
            await message.channel.send(response)
            break

client.run(TOKEN)