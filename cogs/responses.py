from discord.ext import commands

def load_vocabulary(filename):
    vocabulary = set()
    with open(filename, 'r') as file:
        for line in file:
            vocabulary.add(line.strip())
    return vocabulary

class Responses(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None
        self.curse_vocab = load_vocabulary("vocabulary/curses.txt")
        self.grat_vocab = load_vocabulary("vocabulary/gratitude.txt")
    
    async def detect_curses(self, message):
        response = ""
        for word in self.curse_vocab:
            if message.content.upper().find(word) != -1:
                print(f"Detected curse word from {message.author}")
                response += (word.lower() + " ")
        if response != "":
            response = f"{response}ka rin {message.author.mention}!!"
            await message.channel.send(response)
    
    async def detect_gratitude(self, message):
        for word in self.grat_vocab:
            # check if message was replying to bot
            if self.bot.user.id in message.raw_mentions:
                if message.content.upper().find(word) != -1:
                    print(f"Detected thanks from {message.author}")
                    response = f"np bro {message.author.mention}"
                    await message.channel.send(response)
                    break
            elif message.reference is not None:
                if message.reference.cached_message is None:
                    msgref = await message.channel.fetch_message(message.reference.message_id)
                else:
                    msgref = message.reference.cached_message
                if(msgref.author == self.bot.user):
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
    bot.add_cog(Responses(bot))
