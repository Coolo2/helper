from discord.ext import commands 
import discord

import random, os, json
from functions import customerror, functions
from setup import var
from datetime import datetime, timedelta

def getTime():
    return datetime.utcfromtimestamp(int(datetime.now().timestamp()))

class Logging1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    """@commands.Cog.listener()
    async def on_message_delete(self, message):
        print("f")
        desc = message.content

        if desc == "":
            desc = "[Could not get message content]"
        
        if message.author.bot:
            return

        embed = discord.Embed(title="Message Deleted in #" + message.channel.name, description=desc, color=var.embedFail, timestamp=message.created_at)
        embed.set_footer(text="Original message sent at")
        embed.set_author(name="User: " + str(message.author), icon_url=message.author.avatar.url)

        await functions.log(self.bot, message.guild, embed)
    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        
        try:
            if payload.cached_message == None:

                guild = self.bot.get_guild(payload.guild_id)
                channel = guild.get_channel(payload.channel_id)
                
                desc = "[Could not get message content or user]"

                embed = discord.Embed(title="Message Deleted in #" + channel.name, description=desc, color=var.embedFail, timestamp=getTime())

                await functions.log(self.bot, guild, embed)
        except Exception as e:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        
        if after.author.bot:
            return

        embed = discord.Embed(title="Message Deleted in #" + after.channel.name, 
            description=f"[Jump to message](https://discord.com/channels/{after.guild.id}/{after.channel.id}/{after.id})", color=var.embed, timestamp=before.created_at)
        embed.add_field(name="Before:", value= before.content, inline=False)
        embed.add_field(name="After:", value= after.content, inline=False)
        embed.set_footer(text="Original message sent at")
        embed.set_author(name="User: " + str(after.author), icon_url=after.author.avatar.url)

        await functions.log(self.bot, after.guild, embed)"""
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(title="Channel created", color=var.embedSuccess, timestamp=getTime())
        embed.add_field(name="Channel:", value= "<#" + str(channel.id) + ">", inline=False)

        await functions.log(self.bot, "channelCreate", channel.guild, embed)
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        embed = discord.Embed(title="Channel deleted", color=var.embedFail, timestamp=getTime())
        embed.add_field(name="Channel:", value= "#" + channel.name, inline=False)

        await functions.log(self.bot, "channelDelete", channel.guild, embed)
    
    """@commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        embed = discord.Embed(title="Bulk messages deleted", description=str(len(messages)) + " messages deleted", color=var.embedFail, timestamp=getTime())
        embed.add_field(name="Channel:", value= "<#" + str(messages[0].channel.id) + ">", inline=False)

        await functions.log(self.bot, messages[0].guild, embed)"""
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(title="Role created", description="<@&" + str(role.id) + ">", color=var.embedSuccess, timestamp=getTime())

        await functions.log(self.bot, "roleCreate", role.guild, embed)
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(title="Role deleted", description=role.name, color=var.embedFail, timestamp=getTime())

        await functions.log(self.bot, "roleDelete", role.guild, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = discord.Embed(title="User nickname changed", description="<@" + str(after.id) + ">", color=var.embed, timestamp=getTime())
            
            embed.add_field(name="Before:", value= before.name + " (username)" if before.nick == None else before.nick, inline=False)
            embed.add_field(name="After:", value= after.name + " (reset)" if after.nick == None else after.nick, inline=False)

            embed.set_author(name="User: " + str(before), icon_url=after.avatar.url)

            await functions.log(self.bot, "nicknameChange", after.guild, embed)


def setup(bot):
    bot.add_cog(Logging1(bot))