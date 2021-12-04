from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime, timedelta

from discord.commands import slash_command, Option

class Moderation2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="mute", description="Mute a member")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def mute(
        self, 
        ctx, 
        member : Option(discord.Member, description="The member to mute"), 
        length : Option(str, description="The time to mute for (leave blank for infinite)", required=False) = None
    ):
        embed = await functions.mute(self.bot, ctx.guild, member, length)
        await ctx.respond(embed=embed)
        
    
    @slash_command(name="unmute", description="Unmute a member")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def unmute(
        self, 
        ctx, 
        member : Option(discord.Member, description="The member to unmute")
    ):
        embed = await functions.unmute(ctx.guild, member)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Moderation2(bot))