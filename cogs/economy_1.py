from discord.ext import commands 
import discord

import random, os, json
from functions import functions, cooldowns
from setup import var
import helper

import datetime

from discord import app_commands

cooldown = cooldowns.Cooldowns()

class Economy1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="work", description="Get money every 30 seconds")
    @app_commands.guild_only()
    async def work(self, ctx : discord.Interaction):
        cd = cooldown.doCooldown(datetime.timedelta(seconds=30), "work", ctx.user)
        if cd != True:
            raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to work again.")

        balances = await functions.read_data("databases/economy.json")
        money = random.randint(25, 125)

        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.user.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.user.id)] = {"balance":0}

        balances[str(ctx.guild.id)][str(ctx.user.id)]["balance"] += money

        with open(r'resources/workreplies.json') as f:
            reply = random.choice(json.load(f)).replace("{amount}", "**" + str(money) + "**")

        embed = discord.Embed(title=random.choice(["You got money!", "Your paycheck...", "You worked!"]), 
            description="{}! You are now on **{}** credits!".format(reply, balances[str(ctx.guild.id)][str(ctx.user.id)]["balance"]), color=var.embed)
        
        await ctx.response.send_message(embed=embed)

        await functions.save_data("databases/economy.json", balances)
    
    @app_commands.command(name='flip', description="Predict a coin flip correctly and you get credits! Otherwise...")
    @app_commands.describe(guess="Heads or Tails")
    @app_commands.choices(guess=[app_commands.Choice(name="Heads", value="heads"), app_commands.Choice(name="Tails", value="tails")])
    @app_commands.guild_only()
    async def flip(self, ctx : discord.Interaction, guess : str):

        if guess.lower() != "heads" and guess.lower() != "tails":
            raise helper.errors.MildErr(f"Your guess must be 'heads' or 'tails', not '{guess}'")

        botChoice = random.randint(0,1)
        choices = ["heads", "tails"]
        ans = choices[botChoice]

        if ans == guess:
            returnCredits = random.randint(25, 100)
        else:
            returnCredits = random.randint(-75, -25)

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.user.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.user.id)] = {"balance":0}

        balances[str(ctx.guild.id)][str(ctx.user.id)]["balance"] += returnCredits

        if ans == guess:
            embed = discord.Embed(title="You win!", description=f"I got: **{ans}**, You chose: **{guess}**", color=var.embedSuccess)
            embed.add_field(name="Credits", value= f"You got **{returnCredits}** credits! You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits!", inline = False)
        
        else:
            embed = discord.Embed(title="You lose!", description=f"I got: **{ans}**, You chose: **{guess}**", color=var.embedFail)
            embed.add_field(name="Credits", value= f"You lost **{0-returnCredits}** credits! You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits!", inline = False)
                                        
        await ctx.response.send_message(embed=embed)
        await functions.save_data("databases/economy.json", balances)
    
    @app_commands.command(name='roll', description="Predict a dice roll correctly and you get credits! Otherwise...")
    @app_commands.describe(guess="Your dice roll guess from 1-6")
    @app_commands.guild_only()
    async def roll(self, ctx : discord.Interaction, guess : app_commands.Range[int, 1, 6]):

        botChoice = random.randint(1,6)

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.user.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.user.id)] = {"balance":0}

        if botChoice == guess:
            returnCredits = random.randint(25, 200)

            balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] += returnCredits

            embed = discord.Embed(title="You win!", description=f"I got: **{botChoice}**, You chose: **{guess}**", color=var.embedSuccess)
            embed.add_field(name="Credits", value= f"You got **{returnCredits}** credits! You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits!", inline = False)
        else:
            returnCredits = random.randint(-65, -25)

            balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] += returnCredits

            embed = discord.Embed(title="You lost!", description=f"I got: **{botChoice}**, You chose: **{guess}**", color=var.embedFail)
            embed.add_field(name="Credits", value= f"You lost **{0-returnCredits}** credits. You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits.", inline = False)
        
        await ctx.response.send_message(embed=embed)
        await functions.save_data("databases/economy.json", balances)
    
    @app_commands.command(name='rps', description="Play rock, paper, scissors!")
    @app_commands.describe(choice="Your choice for rock, paper or scissors")
    @app_commands.choices(choice=[
            app_commands.Choice(name="Rock", value="rock"), 
            app_commands.Choice(name="Paper", value="paper"), 
            app_commands.Choice(name="Scissors", value="scissors")
    ])
    @app_commands.guild_only()
    async def rps(self, ctx : discord.Interaction, choice : str):
        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.user.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.user.id)] = {"balance":0}

        choices = {"1":"rock","2":"paper","3":"scissors"}
        correct = [ [2, 1], [3, 2], [1, 3] ]

        botChoice = random.randint(1, 3)

        originalGuess = choice
        guess = 1 if choice == "rock" else 2 if choice == "paper" else 3 if choice == "scissors" else None

        for valid in correct:
            if guess in valid:
                embed = ""
                if valid[0] == guess and valid[1] == botChoice:
                    returnCredits = random.randint(25, 200)

                    embed = discord.Embed(title="You win!", description=f"I chose: **{choices[str(botChoice)].title()}**, You chose: **{originalGuess.title()}**", color=var.embedSuccess)
                    embed.add_field(name="Credits", value= f"You got **{returnCredits}** credits! You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] + returnCredits}** credits!", inline = False)
                elif guess == botChoice:
                    embed = discord.Embed(title="Draw!", description=f"I chose: **{choices[str(botChoice)].title()}**, You chose: **{originalGuess.title()}**", color=var.embed)
                    embed.add_field(name="Credits", value= f"You did not gain or lose any credits.", inline = False)
                else:
                    returnCredits = random.randint(-65, -25)

                    embed = discord.Embed(title="You lost!", description=f"I chose: **{choices[str(botChoice)].title()}**, You chose: **{originalGuess.title()}**", color=var.embedFail)
                    embed.add_field(name="Credits", value= f"You lost **{0-returnCredits}** credits. You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] + returnCredits}** credits.", inline = False)
                
                if embed != "":
                    return await ctx.response.send_message(embed=embed)
        
        balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] += returnCredits
        await functions.save_data("databases/economy.json", balances)

    
    @app_commands.command(name="extrawork", description="Work once every 10 minutes and get big rewards!")
    @app_commands.guild_only()
    async def extrawork(self, ctx : discord.Interaction):
        cd = cooldown.doCooldown(datetime.timedelta(minutes=10), "extrawork", ctx.user)
        if cd != True:
            raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to work again.")
        
        balances = await functions.read_data("databases/economy.json")
        money = random.randint(125, 500)
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.user.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.user.id)] = {"balance":0}

        balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] += money

        with open(r'resources/workreplies.json') as f:
            reply = random.choice(json.load(f)).replace("{amount}", "**" + str(money) + "**")

        embed = discord.Embed(title="You got money!", description=f"{reply}! You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits!", color=var.embed)
        await ctx.response.send_message(embed=embed)

        await functions.save_data("databases/economy.json", balances)
    
    @app_commands.command(name="slots", description="Play slots")
    @app_commands.guild_only()
    async def slots(self, ctx : discord.Interaction):
        cd = cooldown.doCooldown(datetime.timedelta(seconds=5), "slots", ctx.user)
        if cd != True:
            raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to use the slot machine again.")
        choices=["", "🍌", "🍉", "🍒", "🍏"]

        choice1 = choices[random.randint(1, 4)]
        choice2 = choices[random.randint(1, 4)]
        choice3 = choices[random.randint(1, 4)]

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.user.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.user.id)] = {"balance":0}

        losses = random.randint(-75, -15) 
        money = random.randint(60, 325)

        if choice1 == choice2 and choice2 == choice3:
            balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] += money

            embed = discord.Embed(title="You win!", description=f"{choice1}|{choice2}|{choice3}", color=var.embedSuccess)
            embed.add_field(name="Credits", value= f"You won **{money}** credits. You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits.", inline = False)
        else:
            balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] += losses

            embed = discord.Embed(title="You lose.", description=f"{choice1}|{choice2}|{choice3}", color=var.embedFail)
            embed.add_field(name="Credits", value= f"You lost **{0-losses}** credits. You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits.", inline = False)
            
        await ctx.response.send_message(embed=embed)

        await functions.save_data("databases/economy.json", balances)
    
    @app_commands.command(name="rob", description="Rob a user")
    @app_commands.describe(member="The member to attempt a robbery on")
    @app_commands.guild_only()
    async def rob(self, ctx : discord.Interaction, member : discord.Member):
        cd = cooldown.doCooldown(datetime.timedelta(hours=1), "rob", ctx.user)
        if cd != True:
            raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to rob again.")
        
        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.user.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.user.id)] = {"balance":0}

        if str(member.id) not in balances[str(ctx.guild.id)] or balances[str(ctx.guild.id)][str(member.id)]['balance'] <= 0:
            cooldown.clearCooldown("rob", ctx.user)
            raise helper.errors.MildErr(f"**{member}** has no money, you can't rob them!")
        if member == ctx.user:
            cooldown.clearCooldown("rob", ctx.user)
            raise helper.errors.MildErr("You can't rob yourself.")

        successfulChance = random.randint(1,3)
        removeAmount = round(balances[str(ctx.guild.id)][str(member.id)]['balance'] / random.randint(4,10))
        fine = round(removeAmount / random.randint(1,3))

        if successfulChance == 1:
            balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] += removeAmount
            balances[str(ctx.guild.id)][str(member.id)]['balance'] -= removeAmount

            embed = discord.Embed(title="You robbed successfully!", description=f"You robbed **{removeAmount}** credits, you are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits, they are now on **{balances[str(ctx.guild.id)][str(member.id)]['balance']}** credits.", color=var.embedSuccess)
            await ctx.response.send_message(embed=embed)

            try:
                embed = discord.Embed(title="Uh-oh! You have been robbed!", description=f"You got robbed **{removeAmount}** credits, you are now on **{balances[str(ctx.guild.id)][str(member.id)]['balance']}** credits.", color=var.embedFail)
                await member.send(embed=embed)
            except Exception as e:
                pass
        else:
            balances[str(ctx.user.id)] -= fine

            embed = discord.Embed(title="You got fined!", description=f"You got fined **{fine}** credits, you are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits.", color=var.embedFail)
            await ctx.response.send_message(embed=embed)
        
        await functions.save_data("databases/economy.json", balances)

async def setup(bot : commands.Bot):
    await bot.add_cog(Economy1(bot))