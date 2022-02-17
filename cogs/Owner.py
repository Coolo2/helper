from discord.ext import commands 
import discord

import random, os, json
from functions import customerror, functions, google
from setup import var
from datetime import datetime, timedelta

from discord.commands import slash_command, Option, permissions

class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name='load', guild_ids=var.guilds, hidden=True)
    @permissions.is_owner()
    async def cogload(self, ctx, *, cog: str):
        cog = "cogs." + cog.replace("cogs.", "")
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @slash_command(name='unload', guild_ids=var.guilds, hidden=True)
    @permissions.is_owner()
    async def cogunload(self, ctx, *, cog: str):
        cog = "cogs." + cog.replace("cogs.", "")
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @slash_command(name='reload', guild_ids=var.guilds, hidden=True)
    @permissions.is_owner()
    async def cogreload(self, ctx, *, cog: str):
        cog = "cogs." + cog.replace("cogs.", "")
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')


    @slash_command(
        name="blacklist", 
        hidden=True, 
        default_permission=False, 
        guild_ids=var.guilds,
        permissions=[permissions.CommandPermission(id=userid, type=2, permission=True) for userid in var.botAdmins]
    )
    async def blacklist(self, ctx, member : discord.Member, *, reason):
        if ctx.author.id in var.botAdmins:
            if member.id not in var.botAdmins:
                with open('databases/blacklist.json') as f:
                    prefixes = json.load(f)
                prefixes[str(member.id)] = reason 
                with open('databases/blacklist.json', 'w') as f:
                    json.dump(prefixes, f, indent=4)
                await ctx.send("> Successfully blacklisted {}".format(member))
            else:
                raise customerror.MildErr("> You cannot blacklist a bot admin")
        else:
            raise customerror.MildErr("> You must be a bot admin to use this command.")

    @slash_command(
        name="whitelist", 
        hidden=True, 
        aliases=['unblacklist'], 
        default_permission=False, 
        guild_ids=var.guilds,
        permissions=[permissions.CommandPermission(id=userid, type=2, permission=True) for userid in var.botAdmins]
    )
    async def unblacklist(self, ctx, member : discord.Member):
        if ctx.author.id in var.botAdmins:
            with open('databases/blacklist.json') as f:
                prefixes = json.load(f)
            del prefixes[str(member.id)] 
            with open('databases/blacklist.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.send("> Successfully whitelisted {}".format(member))
        else:
            raise customerror.MildErr("> You must be a bot admin to use this command.")
    

def setup(bot):
    bot.add_cog(Owner(bot))