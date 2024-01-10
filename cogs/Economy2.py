from discord.ext import commands 
import discord
import random
import datetime

from functions import functions, cooldowns
from setup import var
import helper

from discord import app_commands

cooldown = cooldowns.Cooldowns()

class Economy2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="leaderboard", description="Get the servers leaderboard")
    @commands.guild_only()
    @app_commands.guild_only()
    async def leaderboard(self, ctx : discord.Interaction):
        await ctx.response.defer()

        balances = await functions.read_data("databases/economy.json")
        balanceList = [ k for k, v in sorted(balances[str(ctx.guild.id)].items(), key=lambda item: item[1]["balance"], reverse=True) ]
        
        lb = ""

        for user in balanceList:

            if ctx.guild.get_member(int(user)) is not None:
                lb = lb + f"{balanceList.index(user) + 1}. <@{user}> - {format(balances[str(ctx.guild.id)][user]['balance'], ',d')}\n"

        embed = discord.Embed(title=f"Here's the leaderboard for {ctx.guild.name}", description=lb, color=var.embed)

        await ctx.followup.send(content=None, embed=embed)
    
    @app_commands.command(name="balance", description="Check account balance")
    @app_commands.describe(member="An optional member to see the balance of ")
    @app_commands.guild_only()
    async def balance(self, ctx : discord.Interaction, member : discord.Member = None):
        if member == None:
            member = ctx.user
        
        balances = await functions.read_data("databases/economy.json")
        balance = 0
        
        if str(ctx.guild.id) in balances and str(member.id) in balances[str(ctx.guild.id)]:
            balance = balances[str(ctx.guild.id)][str(member.id)]['balance']
            
        embed = discord.Embed(title=f"{member.name}'s profile balance", description=f"{('**' + str(member) + '** has') if member != ctx.user else 'You have'} **{balance}** credit{'' if balance == 1 else 's'}!", color=0xFF8700)
        await ctx.response.send_message(embed=embed)
    
    @app_commands.command(name="pay", description="Pay a user")
    @app_commands.describe(member="The member to pay", amount="The amount of money to pay")
    @app_commands.guild_only()
    async def pay(self, ctx : discord.Interaction, member : discord.Member, amount : int):

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.user.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)] [str(ctx.user.id)] = {"balance":0}
        
        if int(amount) <= 0:
            raise helper.errors.MildErr("> You cant pay less than 1 credit!")
        if member == ctx.user:
            raise helper.errors.MildErr("> You cant pay yourself!")
        if int(balances[str(ctx.guild.id)][str(ctx.user.id)]["balance"]) < 1:
            raise helper.errors.MildErr(f"> You're below 0 credits! Do **/work** to get some credits!")
        if int(balances[str(ctx.guild.id)][str(ctx.user.id)]["balance"]) < int(amount):
            raise helper.errors.MildErr(f"> You do not have enough credits! You're on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits!")
        
        if str(member.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(member.id)] = {"balance":0}
        
        balances[str(ctx.guild.id)][str(member.id)]['balance'] += int(amount) 
        balances[str(ctx.guild.id)][str(ctx.user.id)]['balance'] -= int(amount) 

        embed = discord.Embed(title=f"{member} was paid successfully!", description=f"You paid them **{amount}** credits, you are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits, they are now on **{balances[str(ctx.guild.id)][str(member.id)]['balance']}** credits.", color=var.embedSuccess)
        await ctx.response.send_message(embed=embed)

        try:
            embed = discord.Embed(title="You have been paid!", description=f"You have been paid {amount} from {ctx.user}! You are now on {balances[str(ctx.guild.id)][str(member.id)]['balance']} credits!", color=var.embed)
            await member.send(embed=embed)
        except Exception as e:
            pass

        await functions.save_data("databases/economy.json", balances)
    
    @app_commands.command(name="shop", description="Economy shop")
    @app_commands.describe(item="An item to buy from the shop")
    @app_commands.choices(item=[app_commands.Choice(name="Crate", value="crate")])
    @app_commands.guild_only()
    async def _shop(
        self, 
        ctx : discord.Interaction, 
        item : str = None
    ):
        

        costs = {"crate":1000}

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.user.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.user.id)] = {"balance":0}
        
        if item == "crate":
            price = costs["crate"]

            if balances[str(ctx.guild.id)][str(ctx.user.id)]["balance"] < price:
                raise helper.errors.MildErr(f"You do not have enough credits for this item. You have **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits")

            cd = cooldown.doCooldown(datetime.timedelta(seconds=30), "shop-crate", ctx.user)
            if cd != True:
                raise helper.errors.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to buy a crate from the shop again.")

            balances[str(ctx.guild.id)][str(ctx.user.id)]["balance"] -= price

            credits = random.randint(750, 1500)

            balances[str(ctx.guild.id)][str(ctx.user.id)]["balance"] += credits 

            embed = discord.Embed(title="Bought a crate!", description=f"You bought a crate for **{price}** credits and got **{credits}** back! You are now on **{balances[str(ctx.guild.id)][str(ctx.user.id)]['balance']}** credits.", color=var.embedSuccess)

            await ctx.response.send_message(embed=embed)

            await functions.save_data("databases/economy.json", balances)

            return 
        
        embed = discord.Embed(title="Shop", description="The Helper economy shop:", color=var.embed)

        embed.add_field(name=f"Crate ({costs['crate']} credits)", value="Gamble and either get more than you paid for or lose...")

        await ctx.response.send_message(embed=embed)







async def setup(bot):
    await bot.add_cog(Economy2(bot))