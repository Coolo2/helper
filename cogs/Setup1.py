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
    
    @app_commands.command(name="setup")
    async def setup(self, ctx):
        return await ctx.response.send_message(embed=discord.Embed(
            title="Setup has moved!",
            description=f"Setup has moved to the [web dashboard]({var.address}/dashboard#{ctx.guild.id})!",
            colour=var.embed
        ))
    
    @app_commands.command(name="customcommands", description="View all custom commands for the server")
    async def customcommands(self, ctx):
        embed = discord.Embed(title=f"Custom commands for {ctx.guild.name}", color=var.embed)
        
        with open("databases/commands.json") as f:
            customCommands = json.load(f)

        if str(ctx.guild.id) not in customCommands:
            return await ctx.response.send_message(f"This server does not have any custom commands! Add some on the web dashboard (`/dashboard`)!")

        for command in customCommands[str(ctx.guild.id)]:
            value = customCommands[str(ctx.guild.id)][command][0:60] + ("..." if len(customCommands[str(ctx.guild.id)][command][0:60]) >= 60 else "")

            embed.add_field(name="/" + command, value=value, inline=False)
        
        embed.add_field(name="... +More", value=f"View more and edit custom commands on the [Web Dashboard]({var.address}/dashboard)", inline=False)

        await ctx.response.send_message(embed=embed)
            
        

async def setup(bot):
    await bot.add_cog(Setup1(bot))