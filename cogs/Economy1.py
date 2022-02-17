from discord.ext import commands 
import discord

import random, os, json
from functions import customerror, functions, cooldowns
from setup import var

import datetime

from discord.commands import slash_command, Option

cooldown = cooldowns.Cooldowns()

class Economy1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="work", description="Get money every 30 seconds", aliases=["getmoney"])
    async def work(self, ctx):
        cd = cooldown.doCooldown(datetime.timedelta(seconds=30), "work", ctx.author)
        if cd != True:
            raise customerror.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to work again.")

        balances = await functions.read_data("databases/economy.json")
        money = random.randint(25, 125)
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        balances[str(ctx.author.id)] += money

        with open(r'resources/workreplies.json') as f:
            reply = random.choice(json.load(f)).replace("{amount}", "**" + str(money) + "**")

        embed = discord.Embed(title=random.choice(["You got money!", "Your paycheck...", "You worked!"]), 
            description="{}! You are now on **{}** credits!".format(reply, balances[str(ctx.author.id)]), color=var.embed)
        await ctx.respond(embed=embed)

        await functions.save_data("databases/economy.json", balances)
    
    @slash_command(name='flip', description="Predict a coin flip correctly and you get credits! Otherwise...", aliases=['coin'])
    async def flip(self, ctx, guess : Option(str, description="heads or tails")):

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
                                        
        await ctx.respond(embed=embed)
        await functions.save_data("databases/economy.json", balances)
    
    @slash_command(name='roll', description="Predict a dice roll correctly and you get credits! Otherwise...", aliases=['dice'])
    async def roll(self, ctx, guess : Option(int, description="Your guess from 1-6", min_value=1, max_value=6)):

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

            embed = discord.Embed(title="You lost!", description=f"I got: **{botChoice}**, You chose: **{guess}**", color=var.embedFail)
            embed.add_field(name="Credits", value= f"You lost **{0-returnCredits}** credits. You are now on **{balances[str(ctx.author.id)]}** credits.", inline = False)
        
        await ctx.respond(embed=embed)
        await functions.save_data("databases/economy.json", balances)
    
    @slash_command(name='rps', description="Play rock, paper, scissors!", aliases=['rock-paper-scissors', "rockpaperscissors", "rsp", "spr"])
    async def rps(self, ctx, choice : Option(str, description="Rock, paper or scissors")):
        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        choices = {"1":"rock","2":"paper","3":"scissors"}
        correct = [ [2, 1], [3, 2], [1, 3] ]

        botChoice = random.randint(1, 3)

        originalGuess = choice
        guess = 1 if choice == "rock" else 2 if choice == "paper" else 3 if choice == "scissors" else None

        for valid in correct:
            if guess in valid and guess in valid:
                embed = ""
                if valid[0] == guess and valid[1] == botChoice:
                    returnCredits = random.randint(25, 200)

                    embed = discord.Embed(title="You win!", description=f"I got: **{choices[str(botChoice)].title()}**, You chose: **{originalGuess.title()}**", color=var.embedSuccess)
                    embed.add_field(name="Credits", value= f"You got **{returnCredits}** credits! You are now on **{balances[str(ctx.author.id)] + returnCredits}** credits!", inline = False)
                elif guess == botChoice:
                    embed = discord.Embed(title="Draw!", description=f"I got: **{choices[str(botChoice)].title()}**, You chose: **{originalGuess.title()}**", color=var.embed)
                    embed.add_field(name="Credits", value= f"You did not gain or lose any credits.", inline = False)
                else:
                    returnCredits = random.randint(-65, -25)

                    embed = discord.Embed(title="You lost!", description=f"I got: **{choices[str(botChoice)].title()}**, You chose: **{originalGuess.title()}**", color=var.embedFail)
                    embed.add_field(name="Credits", value= f"You lost **{0-returnCredits}** credits. You are now on **{balances[str(ctx.author.id)] + returnCredits}** credits.", inline = False)
                
                if embed != "":
                    return await ctx.respond(embed=embed)
    
    @slash_command(name="extrawork", description="Work once every 10 minutes and get big rewards!")
    @commands.cooldown(1, 600, commands.BucketType.user)
    async def extrawork(self, ctx):
        cd = cooldown.doCooldown(datetime.timedelta(minutes=10), "extrawork", ctx.author)
        if cd != True:
            raise customerror.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to work again.")
        
        balances = await functions.read_data("databases/economy.json")
        money = random.randint(125, 500)
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        balances[str(ctx.author.id)] += money

        with open(r'resources/workreplies.json') as f:
            reply = random.choice(json.load(f)).replace("{amount}", "**" + str(money) + "**")

        embed = discord.Embed(title="You got money!", description=f"{reply}! You are now on **{balances[str(ctx.author.id)]}** credits!", color=var.embed)
        await ctx.respond(embed=embed)

        await functions.save_data("databases/economy.json", balances)
    
    @slash_command(name="slots", description="Play slots", aliases=["slot", "slot-machine"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slots(self, ctx):
        cd = cooldown.doCooldown(datetime.timedelta(seconds=5), "slots", ctx.author)
        if cd != True:
            raise customerror.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to use the slot machine again.")
        choices=["", "🍌", "🍉", "🍒", "🍏"]

        choice1 = choices[random.randint(1, 4)]
        choice2 = choices[random.randint(1, 4)]
        choice3 = choices[random.randint(1, 4)]

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        losses = random.randint(-75, -15) 
        money = random.randint(60, 325)

        if choice1 == choice2 and choice2 == choice3:
            balances[str(ctx.author.id)] += money

            embed = discord.Embed(title="You win!", description=f"{choice1}|{choice2}|{choice3}", color=var.embedSuccess)
            embed.add_field(name="Credits", value= f"You won **{money}** credits. You are now on **{balances[str(ctx.author.id)]}** credits.", inline = False)
        else:
            balances[str(ctx.author.id)] += losses

            embed = discord.Embed(title="You lose.", description=f"{choice1}|{choice2}|{choice3}", color=var.embedFail)
            embed.add_field(name="Credits", value= f"You lost **{0-losses}** credits. You are now on **{balances[str(ctx.author.id)]}** credits.", inline = False)
            
        await ctx.respond(embed=embed)

        await functions.save_data("databases/economy.json", balances)
    
    @slash_command(name="rob", description="Rob a user", aliases=["steal"])
    async def rob(self, ctx, member : Option(discord.Member)):
        cd = cooldown.doCooldown(datetime.timedelta(hours=1), "slots", ctx.author)
        if cd != True:
            raise customerror.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to rob again.")
        
        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        if str(member.id) not in balances or balances[str(member.id)] <= 0:
            raise customerror.MildErr(f"**{member}** has no money, you can't rob them!")
        if member == ctx.author:
            raise customerror.MildErr("You can't rob yourself.")

        successfulChance = random.randint(1,3)
        removeAmount = round(balances[str(member.id)] / random.randint(4,10))
        fine = round(removeAmount / random.randint(1,3))

        if successfulChance == 1:
            balances[str(ctx.author.id)] += removeAmount
            balances[str(member.id)] -= removeAmount

            embed = discord.Embed(title="You robbed successfully!", description=f"You robbed **{removeAmount}** credits, you are now on **{balances[str(ctx.author.id)]}** credits, they are now on **{balances[str(member.id)]}** credits.", color=var.embedSuccess)
            await ctx.respond(embed=embed)

            try:
                embed = discord.Embed(title="Uh-oh! You have been robbed!", description=f"You got robbed **{removeAmount}** credits, you are now on **{balances[str(member.id)]}** credits.", color=var.embedFail)
                await member.send(embed=embed)
            except:
                pass
        else:
            balances[str(ctx.author.id)] -= fine

            embed = discord.Embed(title="You got fined!", description=f"You got fined **{fine}** credits, you are now on **{balances[str(ctx.author.id)]}** credits.", color=var.embedFail)
            await ctx.respond(embed=embed)
        
        await functions.save_data("databases/economy.json", balances)

def setup(bot):
    bot.add_cog(Economy1(bot))