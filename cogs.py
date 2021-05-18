import discord
from discord.ext import commands
import random

class MainCog(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} has connected to Discord with ID: {self.bot.user.id}!")
        self.bot.command_prefix = f"<@!{self.bot.user.id}> "

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        
        msg = discord.Embed()
        msg.title = ":x: COMMAND FAILED!"
        msg.description = "Sorry di ko keri huhu =(( *sinuntok ang pader*"
        await ctx.send(embed = msg)
        
        raise error

class Polls(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None
    
    def create_poll_embed(self, ctx, contents):
        embed_msg = discord.Embed()
        embed_msg.title = contents[0]
        embed_msg.set_footer(text=f"requested by {ctx.message.author}")
        embed_msg.timestamp = ctx.message.created_at
        embed_msg.color = 0x800000
        # generate poll options
        embed_msg.description = ""
        emojis = ctx.guild.emojis
        for i in range(1, len(contents)):
            embed_msg.description += f"{emojis[i-1]} - {contents[i]}\n"
        return embed_msg

    @commands.command()
    async def poll(self, ctx, *args):
        # error handling
        OPTION_LIMIT = 10
        if(len(args) - 1 > OPTION_LIMIT):
            raise commands.TooManyArguments
        
        if(len(args) - 1 < 2):
            raise commands.UserInputError

        # create and send embedded message
        message = self.create_poll_embed(ctx, args)
        pollmsg = await ctx.send(embed=message)

        # react to embedded message
        emojis = ctx.guild.emojis
        for i in range(1, len(args)):
            await pollmsg.add_reaction(emojis[i-1])
        
        print(f"Poll was created by {ctx.message.author}!")

    @poll.error
    async def poll_error(self, ctx, error):
        print(str(error))
        if isinstance(error, commands.TooManyArguments):
            print("ERROR: Poll has too many arguments!")
            msg = discord.Embed()
            msg.title = ":x: POLL ERROR"
            msg.description = "Dami mong options di naman ako bayad! :angry:"
            await ctx.send(embed = msg)
        if isinstance(error, commands.UserInputError):
            print("ERROR: Poll has too little arguments!")
            msg = discord.Embed()
            msg.title = ":x: POLL ERROR"
            msg.description = "Magpapapoll pero walang options???? :woozy_face:"
            await ctx.send(embed = msg)

    @commands.command()
    async def choose(self, ctx, *args):
        # error handling
        if(len(args) < 2):
            raise commands.UserInputError
        print("test")
        msg = f"Hmmm... let's go with `{random.choice(args)}` nalang"
        await ctx.message.reply(msg)

        print(f"Requested to choose by {ctx.message.author}!")

    @choose.error
    async def choose_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            print("Choosing from too little options!")
            msg = "Wala namang choices..."
            await ctx.message.reply(msg)
    
            

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
        # Check if command was invoked
        ctx = await self.bot.get_context(message)
        if(ctx.valid):
            return
        else:
            if message.author == self.bot.user:
                return
            await self.detect_curses(message)
            await self.detect_gratitude(message)

def setup(bot):
    bot.add_cog(MainCog(bot))
    bot.add_cog(Responses(bot))
    bot.add_cog(Polls(bot))
