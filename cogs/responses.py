from discord.ext import commands
import discord
from datetime import datetime
import pymongo
import os

from pymongo import server

PATH_CURSE_VOCAB = "curse_vocab"
PATH_GRAT_VOCAB = "grat_vocab"
MONGO_TOKEN = os.getenv('MONGO_TOKEN')
DB_NAME = 'hk69'
COLL_VOCAB = 'vocabulary'
GLOBAL_ID = 'global'

def parse_document(document):
    temp = {}
    for item in document:
        server_id = item["server_id"]
        if server_id not in temp:
            temp[server_id] = set()
        temp[server_id].add(item["word"])
    return temp

def get_global_vocabulary(vocabulary):
    return vocabulary[GLOBAL_ID]

def get_server_vocabulary(vocabulary, msg):
    if(msg.guild):
        server_vocabulary = vocabulary.get(str(msg.guild.id))
        if(server_vocabulary):
            return vocabulary.get(str(msg.guild.id))
    return set()

def load_vocabulary(name):
    with pymongo.MongoClient(MONGO_TOKEN) as client:
        db = client.get_database(DB_NAME)
        collection = db.get_collection(COLL_VOCAB)
        document = collection.find_one({"name":name})['content']
        vocabulary = parse_document(document)
        return vocabulary

def update_vocabulary(name, server_id, words, add=True):
    processed_words = [{"server_id": f"{server_id}", "word": word.upper()} for word in words]

    if(add):
        with pymongo.MongoClient(MONGO_TOKEN) as client:
            db = client.get_database(DB_NAME)
            collection = db.get_collection(COLL_VOCAB)
            collection.update_one(
                {"name":name}, 
                {
                    "$push": {
                        "content": { 
                            "$each" : processed_words
                        }
                    }   
                }
            )
    else:
        with pymongo.MongoClient(MONGO_TOKEN) as client:
            db = client.get_database(DB_NAME)
            collection = db.get_collection(COLL_VOCAB)
            collection.update_one(
                {"name":name}, 
                {
                    "$pull": {
                        "content": { 
                            "$in" : processed_words
                        }
                    }   
                }
            )

class Responses(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None
        self.curse_vocab = load_vocabulary(PATH_CURSE_VOCAB)
        self.grat_vocab = load_vocabulary(PATH_GRAT_VOCAB)

    @commands.group()
    async def show(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.CommandInvokeError
    
    def create_show_embed(self, ctx, type, global_list, server_list):
        msg = discord.Embed()
        msg.description = ""
        msg.title = f"{type.upper()} WORDS"
        if(global_list):
            msg.description += f"Global {type.lower()} words:\n*{', '.join(global_list)}*\n"
        if(server_list):
            if(global_list):
                msg.description += "\n"
            msg.description += f"Server {type.lower()} words:\n*{', '.join(server_list)}*\n"
        msg.set_footer(text = f"requested by {ctx.message.author}")
        msg.timestamp = datetime.utcnow()
        return msg

    @show.command(name="curse")
    async def show_curse(self, ctx, *args):
        global_vocabulary = get_global_vocabulary(self.curse_vocab)
        server_vocabulary = get_server_vocabulary(self.curse_vocab, ctx.message)

        # display message
        msg = self.create_show_embed(ctx, ctx.command.name, global_vocabulary, server_vocabulary)
        await ctx.send(embed = msg)
        print("Curse vocabulary was successfully displayed!")

    @commands.group()
    async def add(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.CommandInvokeError

    def create_add_curse_embed(self, ctx, added, thrown):
        msg = discord.Embed()
        msg.description = ""
        if len(added):
            msg.title = ":white_check_mark: CURSES ARE UPDATED!"
            msg.description += f"The following words have been added:\n*{', '.join(added)}*\n"
        else:
            msg.title = ":warning: CURSES ARE RETAINED!"
        if len(thrown):
            if(len(added)):
                msg.description += "\n"
            msg.description += f"The following words already exist:\n*{', '.join(thrown)}*\n"
        msg.set_footer(text = f"updated by {ctx.message.author}")
        msg.timestamp = datetime.utcnow()
        return msg
    
    @add.command(name="curse")
    @commands.has_permissions(administrator=True)
    async def add_curse(self, ctx, *args):
        # check limits
        if(len(args) < 1):
            raise commands.UserInputError

        # filter new words
        added = []
        thrown = []
        checklist = get_global_vocabulary(self.curse_vocab).union(get_server_vocabulary(self.curse_vocab, ctx))
        for word in args:
            if word.upper() not in checklist:
                added.append(word)
                continue
            thrown.append(word)
        
        # update database and reload vocabulary
        if (added):
            update_vocabulary(PATH_CURSE_VOCAB, ctx.guild.id, added)
            self.curse_vocab = load_vocabulary(PATH_CURSE_VOCAB)
        
        # display success message
        msg = self.create_add_curse_embed(ctx, added, thrown)
        await ctx.send(embed = msg)
        print("Curse vocabulary was successfully updated!")

    @commands.group()
    async def remove(self, ctx):
        if not ctx.invoked_subcommand:
            raise commands.CommandInvokeError

    def create_remove_curse_embed(self, ctx, removed, thrown):
        msg = discord.Embed()
        msg.description = ""
        if len(removed):
            msg.title = ":white_check_mark: CURSES ARE UPDATED!"
            msg.description += f"The following words have been removed:\n*{', '.join(removed)}*\n"
        else:
            msg.title = ":warning: CANNOT BE REMOVED!"
        if len(thrown):
            if(len(removed)):
                msg.description += "\n"
            msg.description += f"The following words cannot be removed:\n*{', '.join(thrown)}*\n"
        msg.set_footer(text = f"updated by {ctx.message.author}")
        msg.timestamp = datetime.utcnow()
        return msg
        
    @remove.command(name="curse")
    @commands.has_permissions(administrator=True)
    async def remove_curse(self, ctx, *args):
        # check limits
        if(len(args) < 1):
            raise commands.UserInputError

        # filter existing words words
        removed = []
        thrown = []
        server_vocab = get_server_vocabulary(self.curse_vocab, ctx)
        global_vocab = get_global_vocabulary(self.curse_vocab)
        for word in args:
            if word.upper() in server_vocab and word.upper() not in global_vocab:
                removed.append(word)
                continue
            thrown.append(word)
        
        # update database and reload vocabulary
        if removed:
            update_vocabulary(PATH_CURSE_VOCAB, ctx.guild.id, removed, add=False)
            self.curse_vocab = load_vocabulary(PATH_CURSE_VOCAB)
        
        # display success message
        msg = self.create_remove_curse_embed(ctx, removed, thrown)
        await ctx.send(embed = msg)
        print("Curse vocabulary was successfully updated!")

    async def detect_curses(self, msg):
        response = ""
        checklist = get_global_vocabulary(self.curse_vocab).union(get_server_vocabulary(self.curse_vocab, msg))
        for word in checklist:
            if msg.content.upper().find(word) != -1:
                print(f"Detected curse word from {msg.author}")
                response += (word.lower() + " ")
        if response != "":
            response = f"{response}ka rin {msg.author.mention}!!"
            await msg.channel.send(response)
    
    async def detect_gratitude(self, msg):
        checklist = get_global_vocabulary(self.grat_vocab).union(get_server_vocabulary(self.grat_vocab, msg))
        for word in checklist:
            # check if message was replying to bot
            if self.bot.user.id in msg.raw_mentions:
                if msg.content.upper().find(word) != -1:
                    print(f"Detected thanks from {msg.author}")
                    response = f"np bro {msg.author.mention}"
                    await msg.channel.send(response)
                    break
            elif msg.reference is not None:
                if msg.reference.cached_message is None:
                    msgref = await msg.channel.fetch_message(msg.reference.message_id)
                else:
                    msgref = msg.reference.cached_message
                if(msgref.author == self.bot.user):
                    if msg.content.upper().find(word) != -1:
                        print(f"Detected thanks from {msg.author}")
                        response = f"np bro {msg.author.mention}"
                        await msg.channel.send(response)
                        break  
            
    @commands.Cog.listener("on_message")
    async def process_message(self, msg):
        #print(f"Message detected: '{msg.content}'")
        # Check if command was invoked
        ctx = await self.bot.get_context(msg)
        if(ctx.valid):
            return
        else:
            if msg.author == self.bot.user:
                return
            await self.detect_curses(msg)
            await self.detect_gratitude(msg)

def setup(bot):
    bot.add_cog(Responses(bot))
