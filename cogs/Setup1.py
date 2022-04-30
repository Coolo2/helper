from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions

from discord import app_commands

class Setup1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    """@slash_command(name="prefix", description="Set or get prefix for a server", aliases=['getprefix', 'setprefix', 'get-prefix', 'set-prefix'])
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix : Option(str, description="The prefix to change to", required=False) = None):
        currentPrefix = functions.prefix(ctx.guild)
        data = await functions.read_data("databases/prefixes.json")
        if prefix == None:
            return await ctx.response.send_message(
                    embed=discord.Embed(
                        title=random.choice([f"Here's the prefix for {ctx.guild.name}", "Here's the prefix", f"Here's my prefix for {ctx.guild.name}"]), 
                        description=f"The prefix for {ctx.guild.name} is **{currentPrefix}**",
                        colour=var.embed
                )
            )
        elif prefix == currentPrefix:
            raise customerror.MildErr(f"The prefix for **{ctx.guild.name}** is already set to **{prefix}**!")
        elif prefix in ['reset', var.prefix]:
            if str(ctx.guild.id) in data:
                del data[str(ctx.guild.id)]
                await ctx.response.send_message(
                    embed=discord.Embed(
                        title=random.choice([f"Resetted the prefix for {ctx.guild.name}", "Resetted your prefix!", "Complete!", "Successfully resetted!"]),
                        description=f"Successfully resetted the prefix for **{ctx.guild.name}** to **{var.prefix}**",
                        colour=var.embedSuccess
                    )
                )
            else:
                raise customerror.MildErr(f"The prefix for **{ctx.guild.name}** is already reset to **{var.prefix}**!")
        else:
            data[str(ctx.guild.id)] = prefix
            await ctx.response.send_message(
                embed=discord.Embed(
                    title=random.choice([f"Set the prefix for {ctx.guild.name}", "Set your prefix!", "Complete!", "Successfully set!"]),
                    description=f"Successfully set the prefix for **{ctx.guild.name}** to **{prefix}**",
                    colour=var.embedSuccess
                )
            )
        await functions.save_data("databases/prefixes.json", data)

        await functions.read_load("databases/prefixes.json", data)"""
    
    @app_commands.command(name="setup")
    async def setup(self, ctx):
        return await ctx.response.send_message(embed=discord.Embed(
            title="Setup has moved!",
            description=f"Setup has moved to the [web dashboard]({var.website}/dashboard#{ctx.guild.id})!",
            colour=var.embed
        ))
    
    @app_commands.command(name="customcommands", description="View all custom commands for the server")
    async def customcommands(self, ctx):
        embed = discord.Embed(title=f"Custom commands for {ctx.guild.name}", color=var.embed)
        
        with open("databases/commands.json") as f:
            customCommands = json.load(f)

        if str(ctx.guild.id) not in customCommands:
            return await ctx.response.send_message(f"This server does not have any custom commands! Add some on the web dashboard (`{functions.prefix(ctx.guild)}dashboard`)!")

        for command in customCommands[str(ctx.guild.id)]:
            value = customCommands[str(ctx.guild.id)][command][0:60] + ("..." if len(customCommands[str(ctx.guild.id)][command][0:60]) >= 60 else "")

            embed.add_field(name=command, value=value, inline=False)
        
        embed.add_field(name="More", value=f"View more and edit custom commands on the [Web Dashboard]({var.address}/dashboard)", inline=False)

        await ctx.response.send_message(embed=embed)
            
        

async def setup(bot):
    await bot.add_cog(Setup1(bot), guilds=var.guilds)