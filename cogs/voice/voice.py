import discord
import asyncio
import helpers.youtube_helper as youtube_helper
from helpers.date_time_helper import seconds_to_dhm
from discord.ext import commands


class Voice(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None

    @commands.group()
    async def music(self, ctx):
        #TODO: display subcommand options
        if not ctx.invoked_subcommand:
            raise commands.CommandInvokeError
    
    @music.command()
    async def play(self, ctx, *, arg):
        loop = self.bot.loop or asyncio.get_running_loop()
        stream_data = await loop.run_in_executor(None, youtube_helper.get_stream_data(arg))
        stream_url = stream_data['url']
        stream_title = stream_data['title']
        stream_duration = seconds_to_dhm(stream_data['duration'])

        voice_client = ctx.voice_client
        voice_client.play(discord.FFmpegPCMAudio(stream_url), after = lambda e : None)

        msg = self.create_playing_embed(ctx, stream_title, stream_duration)
        await ctx.send(embed = msg)

    def create_playing_embed(self, ctx, title, duration):
        msg = discord.Embed()
        msg.description = f":musical_note: Now Playing: **{title}** `[{duration}]`" 
        msg.set_footer(text = f"requested by {ctx.message.author}")
        msg.timestamp = ctx.message.created_at
        return msg 

    @play.before_invoke()
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.message.reply("Wala ka naman sa VC...")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

def setup(bot):
    bot.add_cog(Voice(bot))