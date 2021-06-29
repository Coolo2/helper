import discord, random, os, json
from discord.ext import commands
from functions import customerror, functions
from setup import var
from datetime import datetime, timedelta

class Economy1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="work", description="|Get money every 30 seconds", aliases=["getmoney"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def work(self, ctx):
        balances = await functions.read_data("databases/economy.json")
        money = random.randint(25, 125)
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        balances[str(ctx.author.id)] += money

        with open(r'resources/workreplies.json') as f:
            reply = random.choice(json.load(f)).replace("{amount}", "**" + str(money) + "**")

        embed = discord.Embed(title=random.choice(["You got money!", "Your paycheck...", "You worked!"]), 
            description="{}! You are now on **{}** credits!".format(reply, balances[str(ctx.author.id)]), color=var.embed)
        await ctx.send(embed=embed)

        await functions.save_data("databases/economy.json", balances)
    
    @commands.command(name='flip', description="prefixflip [heads/tails]|Predict a coin flip correctly and you get credits! Otherwise...", aliases=['coin'])
    async def flip(self, ctx, guess):

        if guess.lower() != "heads" and guess.lower() != "tails":
            raise customerror.MildErr(f"Your guess must be 'heads' or 'tails', not '{guess}'")

        botChoice = random.randint(0,1)
        choices = ["heads", "tails"]
        ans = choices[botChoice]

        if ans == guess:
            returnCredits = random.randint(25, 100)
        else:
            returnCredits = random.randint(-75, -25)

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        balances[str(ctx.author.id)] += returnCredits

        if ans == guess:
            embed = discord.Embed(title="You win!", description=f"I got: **{ans}**, You chose: **{guess}**", color=var.embedSuccess)
            embed.add_field(name="Credits", value= f"You got **{returnCredits}** credits! You are now on **{balances[str(ctx.author.id)]}** credits!", inline = False)
        
        else:
            embed = discord.Embed(title="You lose!", description=f"I got: **{ans}**, You chose: **{guess}**", color=var.embedFail)
            embed.add_field(name="Credits", value= f"You lost **{0-returnCredits}** credits! You are now on **{balances[str(ctx.author.id)]}** credits!", inline = False)
                                        
        await ctx.send(embed=embed)
        await functions.save_data("databases/economy.json", balances)
    
    @commands.command(name='roll', description="[1-6]|Predict a dice roll correctly and you get credits! Otherwise...", aliases=['dice'])
    async def roll(self, ctx, guess):

        if guess.isdigit() != True or int(guess) > 7 or int(guess) < 1:
            return customerror.MildErr("Please use a valid number from 1 to 6")

        botChoice = random.randint(1,6)

        if str(botChoice) == guess:
            returnCredits = random.randint(25, 100)
        else:
            returnCredits = random.randint(-75, -25)

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        balances[str(ctx.author.id)] += returnCredits

        if str(botChoice) == guess:
            returnCredits = random.randint(25, 200)

            embed = discord.Embed(title="You win!", description=f"I got: **{botChoice}**, You chose: **{guess}**", color=var.embedSuccess)
            embed.add_field(name="Credits", value= f"You got **{returnCredits}** credits! You are now on **{balances[str(ctx.author.id)]}** credits!", inline = False)
        else:
            returnCredits = random.randint(-65, -25)

            mbed = discord.Embed(title="You lost!", description=f"I got: **{botChoice}**, You chose: **{guess}**", color=var.embedFail)
            embed.add_field(name="Credits", value= f"You lost **{0-returnCredits}** credits. You are now on **{balances[str(ctx.author.id)]}** credits.", inline = False)
        
        await ctx.send(embed=embed)
        await functions.save_data("databases/economy.json", balances)
    
    @commands.command(name="extrawork", description="|Work once every 10 minutes and get big rewards!")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def extrawork(self, ctx):
        
        balances = await functions.read_data("databases/economy.json")
        money = random.randint(125, 500)
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        balances[str(ctx.author.id)] += money

        with open(r'resources/workreplies.json') as f:
            reply = random.choice(json.load(f)).replace("{amount}", "**" + str(money) + "**")

        embed = discord.Embed(title="You got money!", description=f"{reply}! You are now on **{balances[str(ctx.author.id)]}** credits!", color=var.embed)
        await ctx.send(embed=embed)

        await functions.save_data("databases/economy.json", balances)




def setup(bot):
    bot.add_cog(Economy1(bot))