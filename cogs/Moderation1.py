from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime

from discord.commands import slash_command, Option

class Moderation1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="kick", description="Kick a member", aliases=['kickmember', 'kick-member'])
    @commands.guild_only()
    async def kick(
        self, 
        ctx, 
        member : Option(discord.Member, description="The member to kick"), 
        reason : Option(str, description="The reason to go in audit logs", required=False) = None
    ):
        if ctx.author.guild_permissions.kick_members and ctx.author.top_role.position > member.top_role.position or ctx.guild.owner == ctx.author:
            try:
                if reason == None:
                    await member.kick()
                else:
                    await member.kick(reason=reason)
            except:
                raise commands.BotMissingPermissions(["kick_members"])
            embed = discord.Embed(title=random.choice(["Kicked successfully!", "Kicked!", "Successfully kicked!"]), description=f"Successfully kicked **{member.display_name}**{' with reason **' if reason != None else ''}{reason + '**' if reason != None else ''}", colour=var.embedSuccess)
            return await ctx.respond(embed=embed)
        else:
            raise commands.MissingPermissions(["kick_members"])
    
    @slash_command(name="ban", description="Ban a member", aliases=['banmember', 'ban-member'])
    @commands.guild_only()
    async def ban(self, ctx, 
        member : Option(discord.Member, description="The member to ban"), 
        reason : Option(str, description="The reason to show in audit logs", required=False) = None
    ):
        if ctx.author.guild_permissions.ban_members and ctx.author.top_role.position > member.top_role.position or ctx.guild.owner == ctx.author:
            try:
                if reason == None:
                    await member.ban()
                else:
                    await member.ban(reason=reason)
            except:
                raise commands.BotMissingPermissions(["ban_members"])
            embed = discord.Embed(title=random.choice(["Banned successfully!", "Banned!", "Successfully banned!"]), description=f"Successfully banned **{member.display_name}**{' with reason **' if reason != None else ''}{reason + '**' if reason != None else ''}", colour=var.embedSuccess)
            return await ctx.respond(embed=embed)
        else:
            raise commands.MissingPermissions(["ban_members"])  
    
    @slash_command(name="purge", description="Purge a specified amount of messages in a channel", aliases=['nuke', 'massdelete', 'clear', 'clearmessages'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, 
        amount : Option(int, description="The amount of messages to purge", min_value=1), 
        member : Option(discord.Member, description="The user filter to remove messages from", required=False) = None
    ):
        if member == None:
            deleted = await ctx.channel.purge(limit=int(amount) + 1)
            await ctx.respond(f"> Deleted {len(deleted) - 1} messages")
        else:
            def is_me(m):
                return m.author == member
            deleted = await ctx.channel.purge(limit=int(amount) + 1, check=is_me)
            await ctx.respond(f"> Deleted {len(deleted) - 1} messages from {member.display_name}")
    
    @slash_command(name='createinvite', description="Simple way to create an invite to the server", aliases=["create-invite"])
    @commands.guild_only()
    @commands.has_permissions(create_instant_invite=True)
    async def createinvite(self, ctx):
        invite = await ctx.channel.create_invite(destination = ctx.channel, xkcd = True)

        embed = discord.Embed(title=random.choice(["I created a new invite!", "Created a new invite", "Created an invite"]), description=str(invite), color=var.embed)
        await ctx.respond(embed=embed)
        


def setup(bot):
    bot.add_cog(Moderation1(bot))