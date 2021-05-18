from os import X_OK
from discord import message
from discord.ext import commands
import discord
from datetime import datetime

PATH_CURSE_VOCAB = "vocabulary/curses.txt"
PATH_GRAT_VOCAB = "vocabulary/gratitude.txt"

def load_vocabulary(filename):
    vocabulary = set()
    with open(filename, 'r') as file:
        for line in file:
            vocabulary.add(line.strip())
    return vocabulary

def update_vocabulary(filename, word):
    with open(filename,'a') as file:
            file.write(f"{word}\n")

class Responses(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None
        self.curse_vocab = load_vocabulary(PATH_CURSE_VOCAB)
        self.grat_vocab = load_vocabulary(PATH_GRAT_VOCAB)

    @commands.group()
    async def add(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.CommandInvokeError

    def create_curse_embed(self, ctx, added, thrown):
        msg = discord.Embed()
        msg.title = ":white_check_mark: CURSES ARE UPDATED!"
        msg.description = ""
        if len(added):
            msg.description += f"The following words have been added:\n*{', '.join(added)}*\n"
        if len(thrown):
            if(len(added)):
                msg.description += "\n"
            msg.description += f"The following words already exist:\n*{', '.join(thrown)}*\n"
        return msg
    
    @add.command()
    async def curse(self, ctx, *args):
        if(len(args) < 1):
            raise commands.UserInputError
        added = []
        thrown = []
        for word in args:
            if word.upper() not in self.curse_vocab:
                update_vocabulary(PATH_CURSE_VOCAB,word.upper())
                added.append(word)
                continue
            thrown.append(word)
        self.curse_vocab = load_vocabulary(PATH_CURSE_VOCAB)
            
        msg = self.create_curse_embed(ctx, added, thrown)
        await ctx.send(embed = msg)

    async def detect_curses(self, msg):
        response = ""
        for word in self.curse_vocab:
            if msg.content.upper().find(word) != -1:
                print(f"Detected curse word from {msg.author}")
                response += (word.lower() + " ")
        if response != "":
            response = f"{response}ka rin {msg.author.mention}!!"
            await msg.channel.send(response)
    
    async def detect_gratitude(self, msg):
        for word in self.grat_vocab:
            # check if message was replying to bot
            if self.bot.user.id in msg.raw_mentions:
                if msg.content.upper().find(word) != -1:
                    print(f"Detected thanks from {msg.author}")
                    response = f"np bro {msg.author.mention}"
                    await msg.channel.send(response)
                    break
            elif msg.reference is not None:
                if msg.reference.cached_message is None:
                    msgref = await msg.channel.fetch_message(msg.reference.message_id)
                else:
                    msgref = msg.reference.cached_message
                if(msgref.author == self.bot.user):
                    print(f"Detected thanks from {msg.author}")
                    response = f"np bro {msg.author.mention}"
                    await msg.channel.send(response)
                    break  
            
    @commands.Cog.listener("on_message")
    async def process_message(self, msg):
        print(f"Message detected: '{msg.content}'")
        # Check if command was invoked
        ctx = await self.bot.get_context(msg)
        if(ctx.valid):
            return
        else:
            if msg.author == self.bot.user:
                return
            await self.detect_curses(msg)
            await self.detect_gratitude(msg)

def setup(bot):
    bot.add_cog(Responses(bot))
