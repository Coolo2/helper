from discord.ext import commands 
import discord

import json
from setup import var
import helper

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
    setup.extras["IGNORE_IN_COMMAND_LISTS"] = True
    
    @app_commands.command(name="customcommands", description="View all custom commands for the server")
    async def customcommands(self, interaction : discord.Interaction):
        embed = discord.Embed(title=f"Custom commands for {interaction.guild.name}", color=var.embed)
        
        with open("databases/commands.json") as f:
            customCommands = json.load(f)

        if str(interaction.guild.id) not in customCommands or len(customCommands[str(interaction.guild.id)]) == 0:
            return await interaction.response.send_message(
                embed=helper.styling.FailEmbed("None found!", f"This server does not have any custom commands!" + (f" Add some on the [web dashboard]({var.address}/dashboard)!" if interaction.user.guild_permissions.manage_guild else ""))
            )

        for command in customCommands[str(interaction.guild.id)]:
            value = customCommands[str(interaction.guild.id)][command][0:60] + ("..." if len(customCommands[str(interaction.guild.id)][command][0:60]) >= 60 else "")

            embed.add_field(name="/" + command, value=value, inline=False)
        
        embed.add_field(name="... +More", value=f"View more and edit custom commands on the [web dashboard]({var.address}/dashboard)", inline=False)

        await interaction.response.send_message(embed=embed)
            
        

async def setup(bot):
    await bot.add_cog(Setup1(bot))