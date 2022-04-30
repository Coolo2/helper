from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime

from discord import app_commands

class Interaction(commands.Cog):
    def __init__(self, bot : discord.Client):
        self.bot = bot
        
    @app_commands.command(name="suggest", description = "Suggest something to add to the bot")
    @app_commands.describe(suggestion="The suggestion to send")
    async def suggest(self, ctx : discord.Interaction, suggestion : str):

        await ctx.response.send_message(f"> **Thanks for suggesting!** You will recieve a DM if your suggestion is verified (allowed to be voted on) in the Discord <{var.server}>")

        embed = discord.Embed(title=f"New suggestion {ctx.user.id}", color=var.embed)
        embed.add_field(name="From user: {}".format(ctx.user), value=suggestion, inline = False)
        embed.set_footer(text=f"Remember to add a response with your {var.prefix}verifySuggestion command.")

        suggestmessage = await self.bot.get_channel(832906475529043978).send(embed=embed)
        await suggestmessage.edit(content=f"Verify this suggestion with `{var.prefix}verifysuggestion {suggestmessage.id}`")

        await suggestmessage.add_reaction("👍")
        await suggestmessage.add_reaction("👎")

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

    @app_commands.command(name="report", description = "Report a bug or issue")
    @app_commands.describe(issue="The issue to report")
    async def report(self, ctx : discord.Interaction, issue : str):

        await ctx.response.send_message("> **Thanks for reporting!**")

        embed = discord.Embed(title="New report", color=var.embed)
        embed.add_field(name="From user: {}".format(ctx.user), value=issue, inline = False)
        embed.set_footer(text=f"Reply with hb/dm {ctx.user.id} [message]")

        await self.bot.get_channel(832906537822584843).send(embed=embed)
            
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
        
async def setup(bot):
    await bot.add_cog(Interaction(bot), guilds=var.guilds)
