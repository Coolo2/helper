from discord.ext import commands 
import discord
import random
import datetime

from functions import customerror, functions, cooldowns
from setup import var

from discord.commands import slash_command, Option

cooldown = cooldowns.Cooldowns()

class Economy2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="leaderboard", description="Get the servers leaderboard", aliases=["lb", "top"])
    @commands.guild_only()
    async def leaderboard(self, ctx):
        embed = discord.Embed(title=f"Here's the leaderboard for {ctx.guild.name}", description="Loading leaderboard...", color=0xFF8700)
        msg = await ctx.respond(embed=embed)
        msg = await msg.original_message()

        balances = await functions.read_data("databases/economy.json")
        balanceList = [ k for k, v in sorted(balances[str(ctx.guild.id)].items(), key=lambda item: item[1]["balance"], reverse=True) ]
        
        lb = ""

        for user in balanceList:

            if ctx.guild.get_member(int(user)) is not None:
                lb = lb + f"{balanceList.index(user) + 1}. <@{user}> - {format(balances[str(ctx.guild.id)][user]['balance'], ',d')}\n"

        embed = discord.Embed(title=f"Here's the leaderboard for {ctx.guild.name}", description=lb, color=var.embed)
        await msg.edit(content=None, embed=embed)
    
    @slash_command(name="balance", description="Check account balance", aliases=["bal", "money", "credits"])
    async def balance(self, ctx, member : Option(discord.Member, description="Optional member to see balance of. Defaults to yourself", required=False) = None):
        if member == None:
            member = ctx.author
        
        balances = await functions.read_data("databases/economy.json")
        balance = 0
        
        if str(ctx.guild.id) in balances and str(member.id) in balances[str(ctx.guild.id)]:
            balance = balances[str(ctx.guild.id)][str(member.id)]['balance']
            
        embed = discord.Embed(title=f"{member.name}'s profile balance", description=f"{('**' + str(member) + '** has') if member != ctx.author else 'You have'} **{balance}** credit{'' if balance == 1 else 's'}!", color=0xFF8700)
        await ctx.respond(embed=embed)
    
    @slash_command(name="pay", description="Pay a user", aliases=["give"])
    async def pay(self, ctx, member : Option(discord.Member), amount : Option(str, description="The amount to pay (all for all your money)")):

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.author.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.author.id)] = {"balance":0}

        if amount == "all":
            amount = balances[str(ctx.guild.id)][str(ctx.author.id)]['balance']
        
        if int(amount) <= 0:
            raise customerror.MildErr("> You cant pay less than 1 credit!")
        if member == ctx.author:
            raise customerror.MildErr("> You cant pay yourself!")
        if int(balances[str(ctx.guild.id)][str(ctx.author.id)]) < 1:
            raise customerror.MildErr(f"> You're below 0 credits! Do **{functions.prefix(ctx.guild)}work** to get some credits!")
        if int(balances[str(ctx.guild.id)][str(ctx.author.id)]) < int(amount):
            raise customerror.MildErr(f"> You do not have enough credits! You're on **{balances[str(ctx.guild.id)][str(ctx.author.id)]['balance']}** credits!")
        
        if str(member.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(member.id)] = {"balance":0}

        
        balances[str(ctx.guild.id)][str(member.id)]['balance'] += int(amount) 
        balances[str(ctx.guild.id)][str(ctx.author.id)]['balance'] -= int(amount) 

        embed = discord.Embed(title=f"{member} was paid successfully!", description=f"You paid them **{amount}** credits, you are now on **{balances[str(ctx.guild.id)][str(ctx.author.id)]['balance']}** credits, they are now on **{balances[str(ctx.guild.id)][str(member.id)]['balance']}** credits.", color=var.embedSuccess)
        await ctx.respond(embed=embed)

        try:
            embed = discord.Embed(title="You have been paid!", description=f"You have been paid {amount} from {ctx.author}! You are now on {balances[str(ctx.guild.id)][str(member.id)]['balance']} credits!", color=var.embed)
            await member.send(embed=embed)
        except:
            pass

        await functions.save_data("databases/economy.json", balances)
    
    @slash_command(name="shop", description="Economy shop")
    async def _shop(
        self, 
        ctx : discord.ApplicationContext, 
        item : Option(str, description="The item to buy from the shop", choices=["crate"], required=False)
    ):
        

        costs = {"crate":1000}

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.guild.id) not in balances:
            balances[str(ctx.guild.id)] = {}
        if str(ctx.author.id) not in balances[str(ctx.guild.id)]:
            balances[str(ctx.guild.id)][str(ctx.author.id)] = {"balance":0}
        
        if item == "crate":
            price = costs["crate"]

            if balances[str(ctx.guild.id)][str(ctx.author.id)]["balance"] < price:
                raise customerror.MildErr(f"You do not have enough credits for this item. You have **{balances[str(ctx.guild.id)][str(ctx.author.id)]['balance']}** credits")

            cd = cooldown.doCooldown(datetime.timedelta(seconds=30), "shop-crate", ctx.author)
            if cd != True:
                raise customerror.CooldownError(f"You are on cooldown! Please wait **{round(cd.total_seconds())}** seconds to buy a crate from the shop again.")

            balances[str(ctx.guild.id)][str(ctx.author.id)]["balance"] -= price

            credits = random.randint(750, 1500)

            balances[str(ctx.guild.id)][str(ctx.author.id)]["balance"] += credits 

            embed = discord.Embed(title="Bought a crate!", description=f"You bought a crate for **{price}** credits and got **{credits}** back! You are now on **{balances[str(ctx.guild.id)][str(ctx.author.id)]['balance']}** credits.", color=var.embedSuccess)

            await ctx.response.send_message(embed=embed)

            await functions.save_data("databases/economy.json", balances)

            return 
        
        embed = discord.Embed(title="Shop", description="The Helper economy shop:", color=var.embed)

        embed.add_field(name=f"Crate ({costs['crate']} credits)", value="Gamble and either get more than you paid for or lose...")

        await ctx.response.send_message(embed=embed)







def setup(bot):
    bot.add_cog(Economy2(bot))