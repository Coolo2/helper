import discord, random, os, json
from discord.ext import commands
from functions import customerror, functions
from setup import var
from datetime import datetime, timedelta


class Economy2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="leaderboard", description="|Get the servers leaderboard", aliases=["lb", "top"])
    @commands.guild_only()
    async def leaderboard(self, ctx):
        embed = discord.Embed(title=f"Here's the leaderboard for {ctx.guild.name}", description="Loading leaderboard...", color=0xFF8700)
        msg = await ctx.send(embed=embed)

        balances = await functions.read_data("databases/economy.json")
        balanceList = [ k for k, v in sorted(balances.items(), key=lambda item: item[1], reverse=True) ]
        
        lb = ""

        for user in balanceList:

            if ctx.guild.get_member(int(user)) is not None:
                lb = lb + f"{balanceList.index(user) + 1}. <@{user}> - {format(balances[user], ',d')}\n"

        embed = discord.Embed(title=f"Here's the leaderboard for {ctx.guild.name}", description=lb, color=var.embed)
        await msg.edit(content=None, embed=embed)
    
    @commands.command(name="balance", description="*[@user]|Check account balance", aliases=["bal", "money", "credits"])
    async def balance(self, ctx, member : discord.Member = None):
        if member == None:
            member = ctx.message.author
        
        balances = await functions.read_data("databases/economy.json")
        balance = 0
        
        if str(member.id) in balances:
            balance = balances[str(member.id)]
            
        embed = discord.Embed(title=f"{member.name}'s profile balance", description=f"{('**' + str(member) + '** has') if member != ctx.author else 'You have'} **{balance}** credit{'' if balance == 1 else 's'}!", color=0xFF8700)
        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Economy2(bot))