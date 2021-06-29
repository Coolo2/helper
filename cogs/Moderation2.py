import discord, random, os, json
from discord.ext import commands
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime, timedelta

class Moderation2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
         
    @commands.command(name="mute", description="[member] *[length]|Mute a member")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member : discord.Member, *, length = None):
        embed = await functions.mute(self.bot, ctx.guild, member, length)
        await ctx.send(embed=embed)
        
    
    @commands.command(name="unmute", description="[member]|Unmute a member")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member : discord.Member):
        embed = await functions.unmute(ctx.guild, member)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Moderation2(bot))