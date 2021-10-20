import discord
import asyncio

from discord import message
import helpers.youtube_helper as youtube_helper
from helpers.date_time_helper import seconds_to_dhm
from discord.ext import commands


class Voice(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None
        self.current_stream_data = None

    @commands.group()
    async def music(self, ctx):
        #TODO: display subcommand options
        if not ctx.invoked_subcommand:
            raise commands.CommandInvokeError
    
    @music.command()
    async def play(self, ctx, *, arg=None):
        # Voice client should always be present!
        voice_client = ctx.voice_client

        if voice_client.is_playing():
            # Add to queue
            None
        
        elif voice_client.is_paused():
            if arg is None:
                voice_client.resume()
            else:
                None
                # add to queue
        else:
            # TODO
            # insert new song after current
            # end current song

            loop = self.bot.loop or asyncio.get_running_loop()
            self.current_stream_data = await loop.run_in_executor(None, lambda: youtube_helper.get_stream_data(arg))
            stream_url = self.current_stream_data['url']

            voice_client.play(discord.FFmpegPCMAudio(stream_url, **youtube_helper.FFMPEG_OPTIONS), after = lambda e : None)

            msg = self.create_playing_embed(ctx)
            await ctx.send(embed = msg)

    def create_playing_embed(self, ctx):
        title = self.current_stream_data['title']
        duration = seconds_to_dhm(self.current_stream_data['duration'])

        msg = discord.Embed()
        msg.title = ":musical_note: Now Playing"
        msg.description = f"**{title}** `[{duration}]`" 
        msg.set_footer(text = f"requested by {ctx.message.author}")
        msg.timestamp = ctx.message.created_at
        return msg 

    @music.command()
    async def pause(self, ctx):
        voice_client = ctx.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            msg = self.create_pausing_embed(ctx)
            await ctx.send(embed = msg)

    def create_pausing_embed(self, ctx):
        title = self.current_stream_data['title']

        msg = discord.Embed()
        msg.title = ":pause_button: Paused"
        msg.description = f"**{title}**" 
        msg.set_footer(text = f"requested by {ctx.message.author}")
        msg.timestamp = ctx.message.created_at
        return msg 
    
    @music.command()
    async def stop(self, ctx):
        voice_client = ctx.voice_client
        if voice_client:
            voice_client.stop()
            msg = self.create_stopping_embed(ctx)
            await ctx.send(embed = msg)

    def create_stopping_embed(self, ctx):
        msg = discord.Embed()
        msg.title = ":stop_button: Stopped"
        msg.description = "The player has been stopped."
        msg.set_footer(text = f"requested by {ctx.message.author}")
        msg.timestamp = ctx.message.created_at
        return msg 
    
    @play.before_invoke
    @stop.before_invoke
    @pause.before_invoke
    async def ensure_voice(self, ctx):
        voice_client = ctx.voice_client
        if ctx.author.voice is None:
            raise commands.CommandError(message = "NoVoiceChannel")
        elif voice_client is None:
            await ctx.author.voice.channel.connect()
        elif voice_client.channel != ctx.author.voice.channel:
            if voice_client.is_playing():
                if ctx.command.name == 'play':
                    raise commands.CommandError(message = "PlayerBusy")
                else:
                    raise commands.CommandError(message = "InvalidVoiceChannel")


    @play.error
    @stop.error
    @pause.error
    async def join_error(self, ctx, error):
        error_message = str(error)
        print(error_message)
        if isinstance(error, commands.CommandError):
            if error_message == "NoVoiceChannel":
                print(f"ERROR: User {ctx.author} is not connected to a voice channel!")
                msg = "Wala ka naman sa VC..."
                await ctx.reply(msg)
            elif error_message == "PlayerBusy":
                print(f"ERROR: Bot is currently playing in another voice channel!")
                msg = f"Busy pa ako. :( Wait ka nalang or sali ka nalang dito: <#{ctx.voice_client.channel.id}>..."
                await ctx.reply(msg)
            elif error_message == "InvalidVoiceChannel":
                print(f"ERROR: Bot is currently playing in another voice channel!")
                msg = f"Sabotage ka ghorl? Nasa ibang VC ako..."
                await ctx.reply(msg)
   
def setup(bot):
    bot.add_cog(Voice(bot))