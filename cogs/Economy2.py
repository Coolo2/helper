from discord.ext import commands 
import discord

from functions import customerror, functions
from setup import var

from discord.commands import slash_command, Option

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
        balanceList = [ k for k, v in sorted(balances.items(), key=lambda item: item[1], reverse=True) ]
        
        lb = ""

        for user in balanceList:

            if ctx.guild.get_member(int(user)) is not None:
                lb = lb + f"{balanceList.index(user) + 1}. <@{user}> - {format(balances[user], ',d')}\n"

        embed = discord.Embed(title=f"Here's the leaderboard for {ctx.guild.name}", description=lb, color=var.embed)
        await msg.edit(content=None, embed=embed)
    
    @slash_command(name="balance", description="Check account balance", aliases=["bal", "money", "credits"])
    async def balance(self, ctx, member : Option(discord.Member, option="Optional member to see balance of. Defaults to yourself", required=False) = None):
        if member == None:
            member = ctx.author
        
        balances = await functions.read_data("databases/economy.json")
        balance = 0
        
        if str(member.id) in balances:
            balance = balances[str(member.id)]
            
        embed = discord.Embed(title=f"{member.name}'s profile balance", description=f"{('**' + str(member) + '** has') if member != ctx.author else 'You have'} **{balance}** credit{'' if balance == 1 else 's'}!", color=0xFF8700)
        await ctx.respond(embed=embed)
    
    @slash_command(name="pay", description="Pay a user", aliases=["give"])
    async def pay(self, ctx, member : Option(discord.Member), amount : Option(int, min_value=1)):

        balances = await functions.read_data("databases/economy.json")
        
        if str(ctx.author.id) not in balances:
            balances[str(ctx.author.id)] = 0

        if amount == "all":
            amount = balances[str(ctx.author.id)]

        if int(amount) <= 0:
            raise customerror.MildError("> You cant pay less than 1 credit!")
        if member == ctx.author:
            raise customerror.MildError("> You cant pay yourself!")
        if int(balances[str(ctx.author.id)]) < 1:
            raise customerror.MildError(f"> You're below 0 credits! Do **{functions.prefix(ctx.guild)}work** to get some credits!")
        if int(balances[str(ctx.author.id)]) < int(amount):
            raise customerror.MildError(f"> You do not have enough credits! You're on **{balances[str(ctx.author.id)]}** credits!")
        
        if str(member.id) not in balances:
            balances[str(member.id)] = 0

        balances[str(member.id)] += int(amount) 
        balances[str(ctx.author.id)] -= int(amount) 

        embed = discord.Embed(title=f"{member} was paid successfully!", description=f"You paid them **{amount}** credits, you are now on **{balances[str(ctx.author.id)]}** credits, they are now on **{balances[str(member.id)]}** credits.", color=var.embedSuccess)
        await ctx.respond(embed=embed)

        try:
            embed = discord.Embed(title="You have been paid!", description=f"You have been paid {amount} from {ctx.author}! You are now on {balances[str(member.id)]} credits!", color=var.embed)
            await member.send(embed=embed)
        except:
            pass

        await functions.save_data("databases/economy.json", balances)



def setup(bot):
    bot.add_cog(Economy2(bot))