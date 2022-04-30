from discord.ext import commands 
import discord

import random, os, json
from functions import customerror, functions, google
from setup import var
from datetime import datetime, timedelta

from discord import app_commands

class Owner(commands.Cog):

    def __init__(self, bot : discord.Client):
        self.bot = bot
    
    @app_commands.command(name='load')
    @app_commands.guilds(discord.Object(var.support_guild_id))
    @app_commands.default_permissions(administrator=True)
    async def cogload(self, ctx : discord.Interaction, cog: str):
        if ctx.user.id != self.bot.owner_id:
            raise customerror.CustomErr("You do not own the bot")
        cog = "cogs." + cog.replace("cogs.", "")
        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.response.send_message(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.response.send_message('**`SUCCESS`**')

    @app_commands.command(name='unload')
    @app_commands.guilds(discord.Object(var.support_guild_id))
    @app_commands.default_permissions(administrator=True)
    async def cogunload(self, ctx, cog: str):
        if ctx.user.id != self.bot.owner_id:
            raise customerror.CustomErr("You do not own the bot")
        cog = "cogs." + cog.replace("cogs.", "")
        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.response.send_message(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.response.send_message('**`SUCCESS`**')

    @app_commands.command(name='reload')
    @app_commands.guilds(discord.Object(var.support_guild_id))
    @app_commands.default_permissions(administrator=True)
    async def cogreload(self, ctx, cog: str):
        if ctx.user.id != self.bot.owner_id:
            raise customerror.CustomErr("You do not own the bot")
        cog = "cogs." + cog.replace("cogs.", "")
        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.response.send_message(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.response.send_message('**`SUCCESS`**')


    @app_commands.command(
        name="blacklist"
    )
    @app_commands.guilds(discord.Object(var.support_guild_id))
    @app_commands.default_permissions(administrator=True)
    async def blacklist(self, ctx, member : discord.Member, reason : str):
        if ctx.user.id in var.botAdmins:
            if member.id not in var.botAdmins:
                with open('databases/blacklist.json') as f:
                    prefixes = json.load(f)
                prefixes[str(member.id)] = reason 
                with open('databases/blacklist.json', 'w') as f:
                    json.dump(prefixes, f, indent=4)
                await ctx.response.send_message("> Successfully blacklisted {}".format(member))
            else:
                raise customerror.MildErr("> You cannot blacklist a bot admin")
        else:
            raise customerror.MildErr("> You must be a bot admin to use this command.")

    @app_commands.command(
        name="whitelist"
    )
    @app_commands.guilds(discord.Object(var.support_guild_id))
    @app_commands.default_permissions(administrator=True)
    async def unblacklist(self, ctx, member : discord.Member):
        if ctx.user.id in var.botAdmins:
            with open('databases/blacklist.json') as f:
                prefixes = json.load(f)
            del prefixes[str(member.id)] 
            with open('databases/blacklist.json', 'w') as f:
                json.dump(prefixes, f, indent=4)
            await ctx.response.send_message("> Successfully whitelisted {}".format(member))
        else:
            raise customerror.MildErr("> You must be a bot admin to use this command.")
    

async def setup(bot):
    await bot.add_cog(Owner(bot), guilds=var.guilds)