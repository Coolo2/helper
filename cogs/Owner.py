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
        if ctx.user.id != var.owner:
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
        if ctx.user.id != var.owner:
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
        if ctx.user.id != var.owner:
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
    
    @app_commands.command(name='dm', description = 'ADMIN ONLY'
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(discord.Object(var.support_guild_id))
    async def dm(self, ctx : discord.Interaction, member: discord.User, message : str):
        if ctx.user.id in var.botAdmins:
            await member.send('[Message from bot admin {}] {}'.format(ctx.user, message))
            await ctx.response.send_message("> Successfully sent a message to **{}**".format(member))
            dm = self.bot.get_user(368071242189897728)
            await dm.send("> <@368071242189897728> DM From admin {} to {}: **{}**".format(ctx.user, member, message))
        else:
            await ctx.response.send_message('> This command is for bot admins only')
    
    @app_commands.command(
        name="verifysuggestion", 
        description = "[suggestionID]|ADMIN ONLY"
    )
    @app_commands.guilds(discord.Object(var.support_guild_id))
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(suggestion_id="The suggestion ID to verify", response="A response to attach")
    async def verifysuggestion(self, ctx : discord.Interaction, suggestion_id : int, response : str = None):
        if ctx.user.id in var.botAdmins:
            chnl = self.bot.get_channel(832906475529043978)
            msg = await chnl.fetch_message(int(suggestion_id))
            embed = msg.embeds[0]
            oldTitle = msg.embeds[0].title

            embed.title = "New suggestion!"
            embed.set_footer(text=f"Make your own suggestion with {var.prefix}suggest!")

            suggestMessage = await self.bot.get_channel(725706516451033108).send(embed=embed)
            await suggestMessage.add_reaction("👍")
            await suggestMessage.add_reaction("👎")
            await msg.delete()

            try:
                user = self.bot.get_user(int(oldTitle.split(" ")[2]))
                await user.send(f"> One of your suggestions was verified by bot admin `{ctx.user}` with {f'response: **{response}**' if response != None else 'no response.'}")
            except Exception as e:
                print(e)
            await ctx.response.send_message("Suggestion verified.")
        else:
            await ctx.response.send_message('> This command is for bot admins only')
    

async def setup(bot : commands.Bot):
    await bot.add_cog(Owner(bot), guilds=[discord.Object(var.support_guild_id)])