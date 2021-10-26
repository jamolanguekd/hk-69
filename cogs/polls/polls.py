import discord
from discord.ext import commands
import random

GLOBAL_DEFAULT_EMOJIS = ("1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟")

class Polls(commands.Cog):
    def __init__ (self, bot):
        self.bot = bot
        self._last_member = None
    
    def create_poll_embed(self, ctx, contents):
        msg = discord.Embed()
        msg.title = contents[0]
        msg.set_footer(text=f"requested by {ctx.message.author}")
        msg.timestamp = ctx.message.created_at
        msg.color = 0x800000
        # generate poll options
        msg.description = ""
        emojis = ctx.guild.emojis + GLOBAL_DEFAULT_EMOJIS
        for i in range(1, len(contents)):
            msg.description += f"{emojis[i-1]} - {contents[i]}\n\n"
        msg.description = msg.description.rstrip()
        return msg

    def create_choose_embed(self, ctx, winning_pick, repeat = False, tiebreaker = False, attempts = 1, count = None, percentages = None):
        msg = discord.Embed()
        msg.title = ":game_die: ROULETTE :game_die:"
        msg.set_footer(text=f"requested by {ctx.message.author}")
        msg.timestamp = ctx.message.created_at
        msg.color = 0x800000

        # generate multi roll results
        if repeat and attempts > 1:
            msg.description = f"Multi-Roll Results ({attempts} rolls):\n\n"
        
            for index, (choice, percentage) in enumerate(percentages.items()):
                is_winner = choice == winning_pick
                if is_winner:
                    msg.description += f"**{index+1}. __`{choice}`__ - [{count[choice]}/{attempts} rolls] ({percentage}%)**\n"
                else:
                    msg.description += f"{index+1}. `{choice}` - [{count[choice]}/{attempts} rolls] ({percentage}%)\n"
            
            if tiebreaker:
                msg.description += "\n *Additional tiebreaker round was held.*"
        
        else:
            msg.description = f"Hmmm... let's go with `{winning_pick}` nalang. :grinning:"

        return msg

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

    @commands.command(aliases = ['roll'])
    async def choose(self, ctx, *args):
        # error handling
        choices = list(set(args))
        if(len(choices) < 2):
            raise commands.UserInputError(message = "InadequateChoices")

        msg = self.create_choose_embed(ctx, winning_pick=random.choice(choices))
        await ctx.message.reply(embed = msg)

        print(f"Requested to solo-choose by {ctx.message.author}!")

    @commands.command(aliases = ['multiroll', 'multi-roll'])
    async def choose_repeat(self, ctx, attempts, *args):
        choices = list(set(args))
        if(len(choices) < 2):
            raise commands.UserInputError(message = "InadequateChoices")

        if not attempts.isdigit():
            raise commands.UserInputError(message = "NotANumber")
        
        if "." in attempts:
            raise commands.UserInputError(message = "NotAnInteger")
        
        attempts = int(attempts)
        
        if(attempts <= 0):
            raise commands.UserInputError(message = "InvalidAttempts")

        elif(attempts == 1):
            msg = self.create_choose_embed(ctx, winning_pick=random.choice(choices))
            await ctx.message.reply(embed = msg)

        else:
            count = {}
            for choice in choices:
                count[choice] = 0

            for i in range(attempts):
                roll = random.choice(choices)
                count[roll] += 1

            max_value = max(count.values());  
            picks = [key for key, value in count.items() if value == max_value]
            winning_pick = max(count, key=count.get)
            total_attempts = attempts
            tiebreaker = False
            if len(picks) > 1:
                # tiebreaker
                tiebreaker = True
                winning_pick = random.choice(picks)
                count[winning_pick] += 1
                total_attempts += 1

            percentage = {}
            for choice in choices:
                percentage[choice] = round((count[choice] / attempts) * 100, 2)
            
            msg = self.create_choose_embed(ctx, winning_pick=winning_pick, repeat=True, tiebreaker = tiebreaker, attempts = total_attempts, count = count, percentages = percentage)
            await ctx.message.reply(embed = msg)

        print(f"Requested to multi-choose by {ctx.message.author}!")

    @choose.error
    async def choose_error(self, ctx, error):
        if isinstance(error, commands.UserInputError):
            print("Choosing from too little options!")
            msg = "Wala namang choices..."
            await ctx.message.reply(msg)

def setup(bot):
    bot.add_cog(Polls(bot))