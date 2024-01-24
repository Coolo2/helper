from discord.ext import commands 
import discord

import json
from setup import var
import helper

from discord import app_commands

class Setup1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hc : helper.HelperClient = bot.hc
    
    @app_commands.command(name="setup")
    async def setup(self, ctx):
        return await ctx.response.send_message(embed=discord.Embed(
            title="Setup has moved!",
            description=f"Setup has moved to the [web dashboard]({var.address}/dashboard#{ctx.guild.id})!",
            colour=var.embed
        ))
    setup.extras["IGNORE_IN_COMMAND_LISTS"] = True
    
    @app_commands.command(name="customcommands", description="View all custom commands for the server")
    async def customcommands(self, interaction : discord.Interaction):
        embed = helper.styling.MainEmbed(f"Custom commands for {interaction.guild.name}")
        
        custom_commands_raw = await self.hc.db.fetchall("SELECT name, value FROM custom_commands WHERE guild=?", (interaction.guild.id,))

        if len(custom_commands_raw) == 0:
            return await interaction.response.send_message(
                embed=helper.styling.FailEmbed("None found!", f"This server does not have any custom commands!" + (f" Add some on the [web dashboard]({var.address}/dashboard)!" if interaction.user.guild_permissions.manage_guild else ""))
            )

        for command in custom_commands_raw:
            embed.add_field(name="/" + command[0], value=command[1][0:60] + ("..." if len(command[1]) > 60 else ""), inline=False)
        
        embed.add_field(name="... +More", value=f"View more and edit custom commands on the [web dashboard]({var.address}/dashboard)", inline=False)

        await interaction.response.send_message(embed=embed)
            
        

async def setup(bot):
    await bot.add_cog(Setup1(bot))