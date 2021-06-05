import discord
from discord.ext import commands
import random

GLOBAL_DEFAULT_EMOJIS = ("1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟")

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
        emojis = ctx.guild.emojis + GLOBAL_DEFAULT_EMOJIS
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
        emojis = ctx.guild.emojis + GLOBAL_DEFAULT_EMOJIS
        print(emojis)
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
        choices = list(set(args))
        if(len(choices) < 2):
            raise commands.UserInputError
        print("test")
        msg = f"Hmmm... let's go with `{random.choice(choices)}` nalang"
        await ctx.message.reply(msg)

        print(f"Requested to choose by {ctx.message.author}!")

    @choose.error
    async def choose_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            print("Choosing from too little options!")
            msg = "Wala namang choices..."
            await ctx.message.reply(msg)

def setup(bot):
    bot.add_cog(Polls(bot))