from discord.ext import commands 
import discord

from functions import functions
from setup import var
from datetime import datetime

import helper

def getTime():
    return datetime.utcfromtimestamp(int(datetime.now().timestamp()))

class Logging1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hc = bot.hc
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        desc = message.content

        if desc == "" or not desc:
            desc = "[Could not get message content]"
        
        if message.author.bot:
            return

        embed = discord.Embed(title="Message Deleted in #" + message.channel.name, description=desc, color=var.embedFail, timestamp=message.created_at)
        embed.set_footer(text="Original message sent at")
        embed.set_author(name="User: " + str(message.author), icon_url=message.author.avatar.url if message.author.avatar else None)

        await functions.log(self.hc, "delete", message.guild, embed)
    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        
        try:
            if payload.cached_message == None:

                guild = self.bot.get_guild(payload.guild_id)
                channel = guild.get_channel(payload.channel_id)
                
                desc = "[Could not get message content or user]"

                embed = discord.Embed(title="Message Deleted in #" + channel.name, description=desc, color=var.embedFail, timestamp=getTime())

                await functions.log(self.hc, "delete", guild, embed)
        except Exception as e:
            pass
    
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        embed = discord.Embed(title="Channel created", color=var.embedSuccess, timestamp=getTime())
        embed.add_field(name="Channel:", value= "<#" + str(channel.id) + ">", inline=False)

        await functions.log(self.hc, "channelCreate", channel.guild, embed)
    
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):

        embed = discord.Embed(title="Channel deleted", color=var.embedFail, timestamp=getTime())
        embed.add_field(name="Channel:", value= "#" + channel.name, inline=False)

        await functions.log(self.hc, "channelDelete", channel.guild, embed)
    
    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        embed = discord.Embed(title="Bulk messages deleted", description="Unknown amount of messages deleted", color=var.embedFail, timestamp=getTime())
        embed.add_field(name="Channel:", value= "<#" + str(messages[0].channel.id) + ">", inline=False)

        await functions.log(self.hc, "delete", messages[0].guild, embed)
    
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(title="Role created", description="<@&" + str(role.id) + ">", color=var.embedSuccess, timestamp=getTime())

        await functions.log(self.hc, "roleCreate", role.guild, embed)
    
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(title="Role deleted", description=role.name, color=var.embedFail, timestamp=getTime())

        await functions.log(self.hc, "roleDelete", role.guild, embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick:
            embed = discord.Embed(title="User nickname changed", description="<@" + str(after.id) + ">", color=var.embed, timestamp=getTime())
            
            embed.add_field(name="Before:", value= before.name + " (username)" if before.nick == None else before.nick, inline=False)
            embed.add_field(name="After:", value= after.name + " (reset)" if after.nick == None else after.nick, inline=False)

            embed.set_author(name="User: " + str(before), icon_url=after.avatar.url if after.avatar else None)

            await functions.log(self.hc, "nicknameChange", after.guild, embed)


async def setup(bot):
    await bot.add_cog(Logging1(bot))