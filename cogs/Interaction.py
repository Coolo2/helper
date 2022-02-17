from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime

from discord.commands import slash_command, Option, permissions

class Interaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @slash_command(name="suggest", description = "Suggest something to add to the bot")
    async def suggest(self, ctx, suggestion : Option(str, description="The suggestion to send")):
        prefix = functions.prefix(ctx.guild)

        await ctx.respond(f"> **Thanks for suggesting!** You will recieve a DM if your suggestion is verified (allowed to be voted on) in the Discord <{var.server}>")

        embed = discord.Embed(title=f"New suggestion {ctx.author.id}", color=var.embed)
        embed.add_field(name="From user: {}".format(ctx.author), value=suggestion, inline = False)
        embed.set_footer(text=f"Remember to add a response with your {var.prefix}verifySuggestion command.")

        suggestmessage = await self.bot.get_channel(832906475529043978).send(embed=embed)
        await suggestmessage.edit(content=f"Verify this suggestion with `{var.prefix}verifySuggestion {suggestmessage.id}`")

        await suggestmessage.add_reaction("👍")
        await suggestmessage.add_reaction("👎")

    @slash_command(
        name="verifysuggestion", 
        description = "[suggestionID]|ADMIN ONLY", 
        guild_ids=var.guilds, 
        default_permission=False, 
        permissions=[permissions.CommandPermission(id=userid, type=2, permission=True) for userid in var.botAdmins]
    )
    async def verifysuggestion(self, ctx, suggestionID : Option(str, name="suggestion_id"), response : Option(str, description="The response to add", required=False)=None):
        if ctx.author.id in var.botAdmins:
            chnl = self.bot.get_channel(832906475529043978)
            msg = await chnl.fetch_message(int(suggestionID))
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
                await user.send(f"> One of your suggestions was verified by bot admin `{ctx.author}` with {f'response: **{response}**' if response != None else 'no response.'}")
            except Exception as e:
                print(e)
            await ctx.respond("Suggestion verified.")
        else:
            await ctx.respond('> This command is for bot admins only')

    @slash_command(name="report", description = "Report a bug or issue")
    async def report(self, ctx, issue : Option(str, description="The issue to report")):
        prefix = functions.prefix(ctx.guild)

        await ctx.respond("> **Thanks for reporting!**")

        embed = discord.Embed(title="New report", color=var.embed)
        embed.add_field(name="From user: {}".format(ctx.author), value=issue, inline = False)
        embed.set_footer(text=f"Reply with hb/dm {ctx.author.id} [message]")

        await self.bot.get_channel(832906537822584843).send(embed=embed)
            
    @slash_command(name='dm', description = 'ADMIN ONLY', 
        guild_ids=var.guilds, 
        default_permission=False, 
        permissions=[permissions.CommandPermission(id=userid, type=2, permission=True) for userid in var.botAdmins])
    async def dm(self, ctx, member: discord.User, message):
        if ctx.author.id in var.botAdmins:
            await member.send('[Message from bot admin {}] {}'.format(ctx.author, message))
            await ctx.respond("> Successfully sent a message to **{}**".format(member))
            dm = self.bot.get_user(368071242189897728)
            await dm.send("> <@368071242189897728> DM From admin {} to {}: **{}**".format(ctx.author, member, message))
        else:
            await ctx.respond('> This command is for bot admins only')
        
def setup(bot):
    bot.add_cog(Interaction(bot))
