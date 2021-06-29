import discord, random, os, json
from discord.ext import commands
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime

class Moderation1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="kick", description="[member] *[reason]|Kick a member", aliases=['kickmember', 'kick-member'])
    @commands.guild_only()
    async def kick(self, ctx, member : discord.Member, *, reason = None):
        if ctx.author.guild_permissions.kick_members and ctx.author.top_role.position > member.top_role.position or ctx.guild.owner == ctx.author:
            try:
                if reason == None:
                    await member.kick()
                else:
                    await member.kick(reason=reason)
            except:
                raise commands.BotMissingPermissions(["kick_members"])
            embed = discord.Embed(title=random.choice(["Kicked successfully!", "Kicked!", "Successfully kicked!"]), description=f"Successfully kicked **{member.display_name}**{' with reason **' if reason != None else ''}{reason + '**' if reason != None else ''}", colour=var.embedSuccess)
            return await ctx.send(embed=embed)
        else:
            raise commands.MissingPermissions(["kick_members"])
    
    @commands.command(name="ban", description="[member] *[reason]|Ban a member", aliases=['banmember', 'ban-member'])
    @commands.guild_only()
    async def ban(self, ctx, member : discord.Member, *, reason = None):
        if ctx.author.guild_permissions.ban_members and ctx.author.top_role.position > member.top_role.position or ctx.guild.owner == ctx.author:
            try:
                if reason == None:
                    await member.ban()
                else:
                    await member.ban(reason=reason)
            except:
                raise commands.BotMissingPermissions(["ban_members"])
            embed = discord.Embed(title=random.choice(["Banned successfully!", "Banned!", "Successfully banned!"]), description=f"Successfully banned **{member.display_name}**{' with reason **' if reason != None else ''}{reason + '**' if reason != None else ''}", colour=var.embedSuccess)
            return await ctx.send(embed=embed)
        else:
            raise commands.MissingPermissions(["ban_members"])  
    
    @commands.command(name="purge", description="[messages] *[member]|Purge a specified amount of messages in a channel", aliases=['nuke', 'massdelete', 'clear', 'clearmessages'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount, *, member : discord.Member = None):
        try:
            if int(amount) < 1:
                raise customerror.MildErr("Invalid number of messages to delete.")
        except:
            raise customerror.MildErr("Invalid number of messages to delete.")
        if member == None:
            deleted = await ctx.channel.purge(limit=int(amount) + 1)
            await ctx.send(f"> Deleted {len(deleted) - 1} messages")
        else:
            def is_me(m):
                return m.author == member
            deleted = await ctx.channel.purge(limit=int(amount) + 1, check=is_me)
            await ctx.send(f"> Deleted {len(deleted) - 1} messages from {member.display_name}")
    
    @commands.command(name='createinvite', description="|Create an invite to the server", aliases=["create-invite"])
    @commands.guild_only()
    @commands.has_permissions(create_instant_invite=True)
    async def createinvite(self, ctx):
        invite = await ctx.message.channel.create_invite(destination = ctx.message.channel, xkcd = True)

        embed = discord.Embed(title=random.choice(["I created a new invite!", "Created a new invite", "Created an invite"]), description=str(invite), color=var.embed)
        await ctx.send(embed=embed)
        


def setup(bot):
    bot.add_cog(Moderation1(bot))