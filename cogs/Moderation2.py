from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime, timedelta

from discord import app_commands

class Moderation2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="mute", description="Mute a member")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member to mute", length="The duration of the mute (leave blank for infinite)")
    async def mute(
        self, 
        ctx : discord.Interaction, 
        member : discord.Member, 
        length : str = None
    ):
        await ctx.response.defer()
        embed = await functions.mute(self.bot, ctx.guild, member, length)
        await ctx.followup.send(embed=embed)
        
    
    @app_commands.command(name="unmute", description="Unmute a member")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member to unmute")
    async def unmute(
        self, 
        ctx : discord.Interaction, 
        member : discord.Member
    ):
        await ctx.response.defer()
        embed = await functions.unmute(ctx.guild, member)
        await ctx.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation2(bot), guilds=var.guilds)