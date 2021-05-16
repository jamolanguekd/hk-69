import discord
from discord.ext import commands

class MainCog(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} has connected to Discord with ID: {self.bot.user.id}!")
        self.bot.command_prefix = f"<@!{self.bot.user.id}> "

class Polls(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def poll(self, ctx, *args):
        print("test")
        await ctx.send(f"You have created a poll with {len(args)} parameters")

class Responses(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None
    
    async def detect_curses(self, message):
        # TODO: Create separate text file for curse_vocab
        curse_vocab = {"TANGINA","GAGO","PAKYU","BWISET"}
        response = ""

        for word in curse_vocab:
            if message.content.upper().find(word) != -1:
                print(f"Detected curse word from {message.author}")
                response += (word.lower() + " ")
        if response != "":
            response = f"{response}ka rin {message.author.mention}!!"
            await message.channel.send(response)
    
    async def detect_gratitude(self, message):
        # TODO: Create separate text file for grat_vocab
        grat_vocab = {"THANKS", "THANK YOU", "SALAMAT", "LAMAT", "TY"}
        
        for word in grat_vocab:
            # check if message was replying to bot or mentions bot
            if message.reference is not None and message.reference.cached_message.author == self.bot.user \
                or self.bot.user.id in message.raw_mentions:
                if message.content.upper().find(word) != -1:
                    print(f"Detected thanks from {message.author}")
                    response = f"np bro {message.author.mention}"
                    await message.channel.send(response)
                    break

    @commands.Cog.listener("on_message")
    async def process_message(self, message):
        print(f"Message detected: '{message.content}'")
        if message.author == self.bot.user:
            return
        await self.detect_curses(message)
        await self.detect_gratitude(message)

def setup(bot):
    bot.add_cog(MainCog(bot))
    bot.add_cog(Responses(bot))
    bot.add_cog(Polls(bot))
