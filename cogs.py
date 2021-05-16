import discord
from discord.ext import commands

class MainCog(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} has connected to Discord with ID: {self.bot.user.id}!")
        self.bot.command_prefix = f"<@!{self.bot.user.id}> "

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            return
        raise error

class Polls(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None
    
    def create_poll_embed(self, ctx, contents):
        embed_msg = discord.Embed()
        embed_msg.title = contents[0]
        embed_msg.description = ""
        emojis = ctx.guild.emojis
        for i in range(1, len(contents)):
            embed_msg.description += f"{emojis[i-1]} - {contents[i]}\n"
        return embed_msg

    @commands.command()
    async def poll(self, ctx, *args):
        print(f"Poll was created by {ctx.message.author}!")
        await ctx.send(f"You have created a poll with {len(args)} parameters: {str(args)}")
        message = self.create_poll_embed(ctx, args)
        await ctx.send(embed=message)
    

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
