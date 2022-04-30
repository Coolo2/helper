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

    

    @app_commands.command(name="report", description = "Report a bug or issue")
    @app_commands.describe(issue="The issue to report")
    async def report(self, ctx : discord.Interaction, issue : str):

        await ctx.response.send_message("> **Thanks for reporting!**")

        embed = discord.Embed(title="New report", color=var.embed)
        embed.add_field(name="From user: {}".format(ctx.user), value=issue, inline = False)
        embed.set_footer(text=f"Reply with hb/dm {ctx.user.id} [message]")

        await self.bot.get_channel(832906537822584843).send(embed=embed)
            
    
        
async def setup(bot):
    await bot.add_cog(Interaction(bot), guilds=var.guilds)
