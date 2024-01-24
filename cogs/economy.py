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
        self.hc : helper.HelperClient = bot.hc
    
    async def get_user_balance(self, guild : discord.Guild, user : discord.User):
        q = await self.hc.db.fetchone("SELECT balance FROM balances WHERE guild=? AND user=?", (guild.id, user.id))
        if not q:
            await self.hc.db.execute("INSERT INTO balances VALUES (?, ?, ?)", (guild.id, user.id, 0))

        return q[0] if q else 0
    
    async def add_user_balance(self, guild : discord.Guild, user : discord.Guild, amount : int):
        await self.hc.db.execute("UPDATE BALANCES SET balance=balance+? WHERE guild=? AND user=?", (amount, guild.id, user.id))

    @app_commands.command(name="work", description="Get money every 30 seconds")
    @app_commands.guild_only()
    async def work(self, interaction : discord.Interaction):
        cd = cooldown.doCooldown(datetime.timedelta(seconds=30), "work", interaction.user)
        if cd != True:
            raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to work again.")

        money = random.randint(25, 125)
        initial_balance = await self.get_user_balance(interaction.guild, interaction.user)

        await self.add_user_balance(interaction.guild, interaction.user, money)

        with open(r'resources/workreplies.json') as f:
            reply = random.choice(json.load(f)).replace("{amount}", f"**{money:,}**")

        embed = helper.styling.MainEmbed(random.choice(["You got money!", "Your paycheck...", "You worked!"]), f"{reply}! You are now on **{initial_balance+money:,}** credits!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='flip', description="Predict a coin flip correctly and you get credits! Otherwise...")
    @app_commands.describe(guess="Heads or Tails")
    @app_commands.choices(guess=[app_commands.Choice(name="Heads", value="heads"), app_commands.Choice(name="Tails", value="tails")])
    @app_commands.guild_only()
    async def flip(self, interaction : discord.Interaction, guess : str):

        if guess.lower() != "heads" and guess.lower() != "tails":
            raise helper.errors.MildErr(f"Your guess must be 'heads' or 'tails', not '{guess}'")

        botChoice = random.randint(0,1)
        choices = ["heads", "tails"]
        ans = choices[botChoice]

        if ans == guess:
            returnCredits = random.randint(25, 100)
        else:
            returnCredits = random.randint(-75, -25)

        initial_balance = await self.get_user_balance(interaction.guild, interaction.user)
        await self.add_user_balance(interaction.guild, interaction.user, returnCredits)
        
        if ans == guess:
            embed = helper.styling.SuccessEmbed("You win!", f"I got: **{ans}**, You chose: **{guess}**")
            embed.add_field(name="Credits", value= f"You got **{returnCredits:,}** credits! You are now on **{initial_balance+returnCredits:,}** credits!", inline = False)
        
        else:
            embed = helper.styling.FailEmbed("You lose!", f"I got: **{ans}**, You chose: **{guess}**")
            embed.add_field(name="Credits", value= f"You lost **{0-returnCredits:,}** credits! You are now on **{initial_balance+returnCredits:,}** credits!", inline = False)
                                        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='roll', description="Predict a dice roll correctly and you get credits! Otherwise...")
    @app_commands.describe(guess="Your dice roll guess from 1-6")
    @app_commands.guild_only()
    async def roll(self, interaction : discord.Interaction, guess : app_commands.Range[int, 1, 6]):

        botChoice = random.randint(1,6)

        initial_balance = await self.get_user_balance(interaction.guild, interaction.user)

        if botChoice == guess:
            returnCredits = random.randint(25, 200)
            embed = helper.styling.SuccessEmbed("You win!", f"I got: **{botChoice}**, You chose: **{guess}**")
            embed.add_field(name="Credits", value= f"You got **{returnCredits:,}** credits! You are now on **{initial_balance+returnCredits:,}** credits!", inline = False)
        else:
            returnCredits = random.randint(-65, -25)
            embed = helper.styling.FailEmbed("You lost!", f"I got: **{botChoice}**, You chose: **{guess}**")
            embed.add_field(name="Credits", value= f"You lost **{0-returnCredits:,}** credits. You are now on **{initial_balance+returnCredits:,}** credits.", inline = False)

        await self.add_user_balance(interaction.guild, interaction.user, returnCredits)

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name='rps', description="Play rock, paper, scissors!")
    @app_commands.describe(choice="Your choice for rock, paper or scissors")
    @app_commands.choices(choice=[
            app_commands.Choice(name="Rock", value="rock"), 
            app_commands.Choice(name="Paper", value="paper"), 
            app_commands.Choice(name="Scissors", value="scissors")
    ])
    @app_commands.guild_only()
    async def rps(self, interaction : discord.Interaction, choice : str):
        initial_balance = await self.get_user_balance(interaction.guild, interaction.user)

        choices = {"1":"rock","2":"paper","3":"scissors"}
        correct = [ [2, 1], [3, 2], [1, 3] ]

        botChoice = random.randint(1, 3)

        originalGuess = choice
        guess = 1 if choice == "rock" else 2 if choice == "paper" else 3 if choice == "scissors" else None
        
        returnCredits = None
        for valid in correct:
            if guess in valid:
                embed = ""
                if valid[0] == guess and valid[1] == botChoice:
                    returnCredits = random.randint(25, 200)

                    embed = helper.styling.SuccessEmbed("You win!", f"I chose: **{choices[str(botChoice)].title()}**, You chose: **{originalGuess.title()}**")
                    embed.add_field(name="Credits", value= f"You got **{returnCredits:,}** credits! You are now on **{initial_balance+returnCredits:,}** credits!", inline = False)
                elif guess == botChoice:
                    embed = helper.styling.MainEmbed("Draw!", f"I chose: **{choices[str(botChoice)].title()}**, You chose: **{originalGuess.title()}**")
                    embed.add_field(name="Credits", value= f"You did not gain or lose any credits.", inline = False)
                else:
                    returnCredits = random.randint(-65, -25)

                    embed = helper.styling.FailEmbed("You lost!", f"I chose: **{choices[str(botChoice)].title()}**, You chose: **{originalGuess.title()}**")
                    embed.add_field("Credits", f"You lost **{0-returnCredits:,}** credits. You are now on **{initial_balance+returnCredits:,}** credits.", inline = False)
                
                if embed != "":
                    if returnCredits: await self.add_user_balance(interaction.guild, interaction.user, returnCredits)
                    return await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="extrawork", description="Work once every 10 minutes and get big rewards!")
    @app_commands.guild_only()
    async def extrawork(self, interaction : discord.Interaction):
        cd = cooldown.doCooldown(datetime.timedelta(minutes=10), "extrawork", interaction.user)
        if cd != True:
            raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to work again.")
        
        initial_balance = await self.get_user_balance(interaction.guild, interaction.user)
        money = random.randint(125, 500)

        await self.add_user_balance(interaction.guild, interaction.user, money)

        with open(r'resources/workreplies.json') as f:
            reply = random.choice(json.load(f)).replace("{amount}", f"**{money:,}**")

        embed = helper.styling.MainEmbed("You got money!", f"{reply}! You are now on **{initial_balance+money:,}** credits!")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="slots", description="Play slots")
    @app_commands.guild_only()
    async def slots(self, interaction : discord.Interaction):
        cd = cooldown.doCooldown(datetime.timedelta(seconds=5), "slots", interaction.user)
        if cd != True:
            raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to use the slot machine again.")
        choices=["", "🍌", "🍉", "🍒", "🍏"]

        choice1 = choices[random.randint(1, 4)]
        choice2 = choices[random.randint(1, 4)]
        choice3 = choices[random.randint(1, 4)]

        initial_balance = await self.get_user_balance(interaction.guild, interaction.user)

        if choice1 == choice2 and choice2 == choice3:
            money = random.randint(60, 325)
            embed = helper.styling.SuccessEmbed("You win!", f"{choice1}|{choice2}|{choice3}")
            embed.add_field(name="Credits", value= f"You won **{money:,}** credits. You are now on **{initial_balance+money:,}** credits.", inline = False)
        else:
            money = random.randint(-75, -15) 
            embed = helper.styling.FailEmbed("You lose.", f"{choice1}|{choice2}|{choice3}")
            embed.add_field(name="Credits", value= f"You lost **{0-money:,}** credits. You are now on **{initial_balance+money:,}** credits.", inline = False)
        
        await self.add_user_balance(interaction.guild, interaction.user, money)

        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rob", description="Rob a user")
    @app_commands.describe(member="The member to attempt a robbery on")
    @app_commands.guild_only()
    async def rob(self, interaction : discord.Interaction, member : discord.Member):
        cd = cooldown.doCooldown(datetime.timedelta(hours=1), "rob", interaction.user)
        if cd != True:
            raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to rob again.")
        
        other_balance = await self.get_user_balance(interaction.guild, member)
        self_balance = await self.get_user_balance(interaction.guild, interaction.user)

        if other_balance <= 0:
            cooldown.clearCooldown("rob", interaction.user)
            raise helper.errors.MildErr(f"{member.mention} has no money, you can't rob them!")
        if member == interaction.user:
            cooldown.clearCooldown("rob", interaction.user)
            raise helper.errors.MildErr("You can't rob yourself.")

        successfulChance = random.randint(1,3)
        removeAmount = round(other_balance / random.randint(4,10))
        fine = round(removeAmount / random.randint(1,3))

        if successfulChance == 1:
            await self.add_user_balance(interaction.guild, interaction.user, removeAmount)
            await self.add_user_balance(interaction.guild, member, 0-removeAmount)

            embed = helper.styling.SuccessEmbed("You robbed successfully!", f"You robbed **{removeAmount:,}** credits, you are now on **{self_balance+removeAmount:,}** credits, they are now on **{other_balance-removeAmount:,}** credits.")
            await interaction.response.send_message(embed=embed)

            try:
                embed = helper.styling.FailEmbed("Uh-oh! You have been robbed!", f"You got robbed **{removeAmount:,}** credits, you are now on **{other_balance-removeAmount:,}** credits.")
                await member.send(embed=embed)
            except Exception as e:
                pass
        else:
            await self.add_user_balance(interaction.guild, interaction.user, 0-fine)

            embed = helper.styling.FailEmbed("You got fined!", f"You got fined **{fine:,}** credits, you are now on **{self_balance-fine:,}** credits.")
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="leaderboard", description="Get the servers leaderboard")
    @commands.guild_only()
    @app_commands.guild_only()
    async def leaderboard(self, interaction : discord.Interaction):

        balances_raw = await self.hc.db.fetchall("SELECT user, balance FROM balances WHERE guild=?", (interaction.guild.id,))
        balanceList = list(sorted(balances_raw, key=lambda item: item[1], reverse=True))
        
        lb = ""

        for i, balance_raw in enumerate(balanceList):
            if interaction.guild.get_member(int(balance_raw[0])):
                lb = lb + f"{i + 1}. <@{balance_raw[0]}> - {balance_raw[1]:,d}\n"

        embed = helper.styling.MainEmbed(f"Here's the leaderboard for {interaction.guild.name}")

        paginator = helper.paginator.PaginatorView(embed, lb, "\n", 20)

        await interaction.response.send_message(embed=embed, view=paginator)
    
    @app_commands.command(name="balance", description="Check account balance")
    @app_commands.describe(member="An optional member to see the balance of ")
    @app_commands.guild_only()
    async def balance(self, interaction : discord.Interaction, member : discord.Member = None):
        if member == None:
            member = interaction.user
        
        balance = await self.get_user_balance(interaction.guild, member)
            
        embed = helper.styling.MainEmbed(f"{member.name}'s profile balance", f"{('**' + member.mention+ '** has') if member != interaction.user else 'You have'} **{balance:,}** credit{'' if balance == 1 else 's'}!")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="pay", description="Pay a user")
    @app_commands.describe(member="The member to pay", amount="The amount of money to pay")
    @app_commands.guild_only()
    async def pay(self, interaction : discord.Interaction, member : discord.Member, amount : int):

        self_balance = await self.get_user_balance(interaction.guild, interaction.user)
        other_balance = await self.get_user_balance(interaction.guild, member)
        
        if member == interaction.user:
            raise helper.errors.MildErr("> You cant pay yourself!")
        if int(amount) <= 0:
            raise helper.errors.MildErr("> You cant pay less than 1 credit!")
        if self_balance < 1:
            raise helper.errors.MildErr(f"> You're below 0 credits! Do **/work** to get some credits!")
        if self_balance < int(amount):
            raise helper.errors.MildErr(f"> You do not have enough credits! You're on **{self_balance}** credits!")
        
        await self.add_user_balance(interaction.guild, interaction.user, 0-amount)
        await self.add_user_balance(interaction.guild, member, amount)

        embed = helper.styling.SuccessEmbed(f"{member} was paid successfully!", f"You paid {member.mention} **{amount:,}** credits, you are now on **{self_balance-amount:,}** credits, they are now on **{other_balance+amount:,}** credits.")
        await interaction.response.send_message(embed=embed)

        try:
            embed = helper.styling.MainEmbed("You have been paid!", f"You have been paid **{amount:,}** by **{interaction.user}** in **{interaction.guild.name}**! You are now on {other_balance+amount:,} credits!")
            await member.send(embed=embed)
        except Exception as e:
            pass
    
    @app_commands.command(name="shop", description="Economy shop")
    @app_commands.describe(item="An item to buy from the shop")
    @app_commands.choices(item=[app_commands.Choice(name="Crate", value="crate")])
    @app_commands.guild_only()
    async def _shop(
        self, 
        interaction : discord.Interaction, 
        item : str = None
    ):

        costs = {"crate":1000}

        initial_balance = await self.get_user_balance(interaction.guild, interaction.user)
        
        if item == "crate":
            price = costs["crate"]

            if initial_balance < price:
                raise helper.errors.MildErr(f"You do not have enough credits for this item. You have **{initial_balance}** credits and require **{price}**")

            cd = cooldown.doCooldown(datetime.timedelta(seconds=30), "shop-crate", interaction.user)
            if cd != True:
                raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to buy a crate from the shop again.")
            
            credits = random.randint(750, 1250)

            await self.add_user_balance(interaction.guild, interaction.user, 0-price+credits)

            embed = helper.styling.SuccessEmbed("Bought a crate!", f"You bought a crate for **{price:,}** credits and got **{credits:,}** back! You are now on **{initial_balance-costs[item]+credits:,}** credits.")
            await interaction.response.send_message(embed=embed)

            return 
        
        embed = helper.styling.MainEmbed("Shop", "The Helper economy shop:")

        embed.add_field(name=f"Crate ({costs['crate']} credits)", value="Gamble and either get more than you paid for or lose...")

        await interaction.response.send_message(embed=embed)


async def setup(bot : commands.Bot):
    await bot.add_cog(Economy1(bot))