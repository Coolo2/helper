import discord, random, os, json
from discord.ext import commands
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime

class Interaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="suggest", description = "[suggestion]|Suggest something to add to the bot")
    async def suggest(self, ctx, *, suggestion):
        prefix = functions.prefix(ctx.guild)

        await ctx.send(f"> **Thanks for suggesting!** You will recieve a DM if your suggestion is verified (allowed to be voted on) in the Discord <{var.server}>")

        embed = discord.Embed(title=f"New suggestion {ctx.author.id}", color=var.embed)
        embed.add_field(name="From user: {}".format(ctx.message.author), value=suggestion, inline = False)
        embed.set_footer(text=f"Remember to add a response with your {var.prefix}verifySuggestion command.")

        suggestmessage = await self.bot.get_channel(832906475529043978).send(embed=embed)
        await suggestmessage.edit(content=f"Verify this suggestion with `{var.prefix}verifySuggestion {suggestmessage.id}`")

        await suggestmessage.add_reaction("👍")
        await suggestmessage.add_reaction("👎")

    @commands.command(name="verifysuggestion", description = "[suggestionID]|ADMIN ONLY")
    async def verifysuggestion(self, ctx, suggestionID, *, response=None):
        if ctx.message.author.id in var.botAdmins:
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
            await ctx.send("Suggestion verified.")
        else:
            await ctx.send('> This command is for bot admins only')

    @commands.command(name="report", description = "[issue]|Report a bug or issue")
    async def report(self, ctx, *, issue):
        prefix = functions.prefix(ctx.guild)

        await ctx.send("> **Thanks for reporting!**")

        embed = discord.Embed(title="New report", color=var.embed)
        embed.add_field(name="From user: {}".format(ctx.message.author), value=issue, inline = False)
        embed.set_footer(text=f"Reply with hb/dm {ctx.author.id} [message]")

        await self.bot.get_channel(832906537822584843).send(embed=embed)
            
    @commands.command(name='dm', description = 'ADMIN ONLY')
    async def dm(self, ctx, member: discord.User, *, message):
        if ctx.message.author.id in var.botAdmins:
            await member.send('[Message from bot admin {}] {}'.format(ctx.author, message))
            await ctx.send("> Successfully sent a message to **{}**".format(member))
            dm = self.bot.get_user(368071242189897728)
            await dm.send("> <@368071242189897728> DM From admin {} to {}: **{}**".format(ctx.message.author, member, message))
        else:
            await ctx.send('> This command is for bot admins only')
        
def setup(bot):
    bot.add_cog(Interaction(bot))
