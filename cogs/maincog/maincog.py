import discord
from discord.ext import commands

class MainCog(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} has connected to Discord with ID: {self.bot.user.id}!")
        self.bot.command_prefix = [f"<@!{self.bot.user.id}> ",f"<@{self.bot.user.id}> ","hk!"]

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.MissingPermissions):
            msg = discord.Embed()
            msg.title = ":x: COMMAND FAILED!"
            msg.description = "Admin ka ghorl?"
            await ctx.send(embed = msg)
            return
            
        msg = discord.Embed()
        msg.title = ":x: COMMAND FAILED!"
        msg.description = "Sorry di ko keri huhu =(( *sinuntok ang pader*"
        await ctx.send(embed = msg)
        raise error

def setup(bot):
    bot.add_cog(MainCog(bot))