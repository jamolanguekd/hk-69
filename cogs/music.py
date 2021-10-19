import discord
from discord.ext import commands

class Music(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None

    @commands.group()
    async def music(self, ctx):
        #TODO: display subcommand options
        if not ctx.invoked_subcommand:
            raise commands.CommandInvokeError
    
    @music.command()
    async def play(self, ctx):
        voice_channel = ctx.author.voice.channel
        if ctx.author.voice.channel is None:
            msg = "Wala ka naman sa VC"
            await ctx.message.reply(msg)
        else:
            await voice_channel.connect()

def setup(bot):
    bot.add_cog(Music(bot))