from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime

from discord import app_commands

class Moderation1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="kick", description="Kick a member")
    @app_commands.guild_only()
    @app_commands.default_permissions(kick_members=True)
    @app_commands.checks.has_permissions(kick_members=True)
    @app_commands.describe(member="The member to kick", reason="The reason to be added to audit logs")
    async def kick(
        self, 
        ctx : discord.Interaction, 
        member : discord.Member, 
        reason : str = None
    ):
        if ctx.user.guild_permissions.kick_members and ctx.user.top_role.position > member.top_role.position or ctx.guild.owner == ctx.user:
            try:
                if reason == None:
                    await member.kick()
                else:
                    await member.kick(reason=reason)
            except Exception as e:
                raise commands.BotMissingPermissions(["kick_members"])
            embed = discord.Embed(title=random.choice(["Kicked successfully!", "Kicked!", "Successfully kicked!"]), description=f"Successfully kicked **{member.display_name}**{' with reason **' if reason != None else ''}{reason + '**' if reason != None else ''}", colour=var.embedSuccess)
            return await ctx.response.send_message(embed=embed)
        else:
            raise commands.MissingPermissions(["kick_members"])
    
    @app_commands.command(name="ban", description="Ban a member")
    @app_commands.guild_only()
    @app_commands.default_permissions(ban_members=True)
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.describe(member="The member to ban", delete_message_days="Amount of days to delete message history of the banned user", reason="A reason to be added to audit logs")
    async def ban(self, ctx : discord.Interaction, 
        member : discord.Member, 
        delete_message_days : app_commands.Range[int, 0] = None,
        reason : str = None
    ):
        if delete_message_days == None:
            delete_message_days = 0
        if ctx.user.guild_permissions.ban_members and ctx.user.top_role.position > member.top_role.position or ctx.guild.owner == ctx.user:
            try:
                await member.ban(reason=reason, delete_message_days=delete_message_days)
            except Exception as e:
                raise commands.BotMissingPermissions(["ban_members"])
            embed = discord.Embed(title=random.choice(["Banned successfully!", "Banned!", "Successfully banned!"]), description=f"Successfully banned **{member.display_name}**{' with reason **' if reason != None else ''}{reason + '**' if reason != None else ''}", colour=var.embedSuccess)
            return await ctx.response.send_message(embed=embed)
        else:
            raise commands.MissingPermissions(["ban_members"])  
    
    @app_commands.command(name="purge", description="Purge a specified amount of messages in a channel")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(amount="The amount of messages to purge", member="The user filter to remove messages from")
    async def purge(self, ctx : discord.Interaction, 
        amount : app_commands.Range[int, 0], 
        member : discord.Member = None
    ):
        await ctx.response.defer()
        if member == None:
            deleted = await ctx.channel.purge(limit=int(amount) + 1)
            await ctx.followup.send(f"> Deleted {len(deleted) - 1} messages")
        else:
            def is_me(m):
                return m.user == member
            deleted = await ctx.channel.purge(limit=int(amount) + 1, check=is_me)
            await ctx.followup.send(f"> Deleted {len(deleted) - 1} messages from {member.display_name}")
    
    @app_commands.command(name='createinvite', description="Simple way to create an invite to the server")
    @app_commands.guild_only()
    @app_commands.default_permissions(create_instant_invite=True)
    @app_commands.checks.has_permissions(create_instant_invite=True)
    async def createinvite(self, ctx : discord.Interaction):
        invite = await ctx.channel.create_invite()

        embed = discord.Embed(title=random.choice(["I created a new invite!", "Created a new invite", "Created an invite"]), description=str(invite), color=var.embed)
        await ctx.response.send_message(embed=embed)
        


async def setup(bot):
    await bot.add_cog(Moderation1(bot), guilds=var.guilds)