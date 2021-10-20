import discord
import asyncio
import DiscordUtils
import helpers.youtube_helper as youtube_helper
from helpers.date_time_helper import seconds_to_dhm
from discord.ext import commands

PLAYLIST_EMBED_TITLE = ":musical_note: Playlist :musical_note:"
SONGS_PER_PAGE = 5

class Voice(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None
        self.queue = []
        self.current_index = -1
        self.queue_length = 0
        self.current_stream_data = None

    def stringify_queue_list(self, limit):
        queue = self.queue
        length = self.queue_length
        if queue:
            stringified_queue = []
            start = 0
            end = min(length, limit)
            while(True):
                temp = ""
              
                # Parse String Per Page
                for index, item in enumerate(queue[start:end]):
                    temp += f"{index+1}.) {item['title']} [{seconds_to_dhm(item['duration'])}]"
                    if self.current_index == index:
                        temp += "*<--- Current Track*"
                    temp += "\n"

                stringified_queue.append(temp)

                # Adjust boundaries
                start += limit
                end += limit

                # Break Condition
                if start >= length:
                    break
            return stringified_queue
        else:
            return []
    
    def stringify_queue_length(self):
        if self.queue_length:
            return f"*{self.queue_length} tracks in the playlist.*"
        else:
            return "*The playlist is currently empty.*"

    def create_queue_page_embed(self, ctx, song_list):
        msg = discord.Embed()
        msg.title = PLAYLIST_EMBED_TITLE
        msg.description += song_list
        msg.set_footer(text=f"requested by {ctx.message.author}")
        msg.timestamp = ctx.message.created_at
    
    def create_queue_empty_embed(self, ctx):
        msg = discord.Embed()
        msg.title = PLAYLIST_EMBED_TITLE
        msg.description = self.stringify_queue_length()
        msg.set_footer(text=f"requested by {ctx.message.author}")
        msg.timestamp = ctx.message.created_at
        
        return msg

    def create_queue_embeds(self, ctx):
        embeds = []
        stringified_queue = self.stringify_queue_list(SONGS_PER_PAGE)
        if stringified_queue:
            for string in stringified_queue:
                embed = self.create_queue_empty_embed(ctx, string)
                embeds.append(embed)
        else:
            embed = self.create_queue_empty_embed(ctx)
            embeds.append(embed)
        return embeds

    async def show_queue(self, ctx):
        embeds = self.create_queue_embeds(ctx)
        paginator = DiscordUtils.Pagination.AutoEmbedPaginator(ctx)
        paginator.run(embeds)

    async def get_data(self, keyword):
        loop = self.bot.loop or asyncio.get_running_loop()
        self.current_stream_data = await loop.run_in_executor(None, lambda: youtube_helper.get_stream_data(keyword))
        stream_url = self.current_stream_data['url']

    def enqueue(self, stream_data):
        self.queue.append(stream_data)
        self.queue_length += 1
    
    def insert(self, position, stream_data):
        self.queue.insert(position, stream_data)
        self.queue_length += 1

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
            if arg:
                await self.add(ctx, args=arg)
            else:
                raise commands.CommandError(message = "AlreadyPlaying")     
        
        elif voice_client.is_paused():
            if arg:
                await self.add(ctx,args=arg)
            else:
                voice_client.resume()
        else:
            if arg is None:
                raise commands.MissingRequiredArgument
         
            await self.add(ctx, args=arg)
            self.current_index = self.queue_length

            stream_url = self.current_stream_data[self.current_index]['url']
            voice_client.play(discord.FFmpegPCMAudio(stream_url, **youtube_helper.FFMPEG_OPTIONS), after = lambda e : None)

        #msg = self.create_playing_embed(ctx)
        #await ctx.send(embed = msg)
        await self.show_queue(ctx)
 
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
    async def add(self, ctx, *, args = None):
        if args is None:
            raise commands.MissingRequiredArgument
        
        # Add song to queue
        new_stream_data = await self.get_data(args)
        self.enqueue(new_stream_data)

        # Show queue
        await self.show_queue(ctx)


    @music.command()
    async def pause(self, ctx):
        voice_client = ctx.voice_client
        if voice_client.is_playing():
            voice_client.pause()
            msg = self.create_pausing_embed(ctx)
            await ctx.send(embed = msg)
        elif voice_client.is_paused():
            raise commands.CommandError(message = "AlreadyPaused")

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
        if not voice_client.is_playing() and not voice_client.is_paused():
            raise commands.CommandError(message = "AlreadyStopped")
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
                print("ERROR: Bot is currently playing in another voice channel!")
                msg = f"Busy pa ako. :( Wait ka nalang or sali ka nalang dito: <#{ctx.voice_client.channel.id}>..."
                await ctx.reply(msg)
            elif error_message == "InvalidVoiceChannel":
                print("ERROR: Bot is currently playing in another voice channel!")
                msg = "Sabotage ka ghorl? Nasa ibang VC ako..."
                await ctx.reply(msg)
            elif error_message == "AlreadyPaused":
                print("ERROR: Bot has already paused audio")
                msg = "Naka-pause na ako sis,,,"
                await ctx.reply(msg)
            elif error_message == "AlreadyStopped":
                print("ERROR: Bot has already stopped audio")
                msg = "Wala naman akong ginagawa :--/"
                await ctx.reply(msg)
        elif isinstance(error, commands.MissingRequiredArgument):
            command = ctx.command.name
            if command == "play" or command == "add":
                msg = "Anong i-pplay ko??? :weary:"
                await ctx.reply(msg)
   
def setup(bot):
    bot.add_cog(Voice(bot))