
import discord

from discord.ext import commands

import random, json
from discord.app_commands import errors
from functions import functions
from setup import var
from EasyConversion import textformat

import datetime
import helper

class Handling1(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
    
        @bot.tree.error
        async def on_application_command_error(interaction : discord.Interaction, error : Exception):

            if interaction.response.is_done():
                response = interaction.followup.send
            else:
                response = interaction.response.send_message
            
            msgMild = random.choice(["Uh oh!", "Oops!", "Oh no!"])
            msgUnkown = random.choice(["You've ran into an unknown error!", "You've ran into an error!"])
            
            if isinstance(error, commands.MissingRequiredArgument):
                embed = discord.Embed(title=msgMild, description=f"```{error}\n/{interaction.command.name} {interaction.command.description.split('|')[0]}```", colour=var.embedFail, timestamp=datetime.datetime.now())
                return await response(embed=embed, ephemeral=True)
            
            if isinstance(error, commands.NoPrivateMessage):
                embed = discord.Embed(title=msgMild, description=f"```{error}```", colour=var.embedFail, timestamp=datetime.datetime.now())
                return await response(embed=embed, ephemeral=True)
            if isinstance(error, commands.CommandOnCooldown):
                embed = discord.Embed(title=msgMild, description=f"{error}", colour=var.embedFail)
                return await response(embed=embed, ephemeral=True)
            if isinstance(error, errors.CheckFailure):
                embed = discord.Embed(title=msgMild, description=f"t", colour=var.embedFail)
                return await response(embed=embed, ephemeral=True)

            if isinstance(error, errors.CommandInvokeError):
                if isinstance(error.original, commands.MemberNotFound):
                    embed = discord.Embed(title=msgMild, description=f"```{str(error.original)}```", colour=var.embedFail, timestamp=datetime.datetime.now())
                    return await response(embed=embed, ephemeral=True)
                if isinstance(error.original, commands.MissingPermissions):
                    embed = discord.Embed(title=msgMild, description=f"```{error.original}```", colour=var.embedFail, timestamp=datetime.datetime.now())
                    return await response(embed=embed, ephemeral=True)
                if isinstance(error.original, commands.BotMissingPermissions):
                    embed = discord.Embed(title=msgMild, 
                    description=f"```{error.original}\n\nEnsure that I have the above permissions and my role is high enough to use /{interaction.command.name}```", 
                    colour=var.embedFail, timestamp=datetime.datetime.now())
                    return await response(embed=embed, ephemeral=True)
                if isinstance(error.original, errors.CheckFailure):
                    embed = discord.Embed(title=msgMild, description=f"t", colour=var.embedFail)
                    return await response(embed=embed, ephemeral=True)

                # Custom errors
                if isinstance(error.original, helper.errors.CustomErr):
                    embed = discord.Embed(title=msgMild, description=f"```{error.original}```", colour=var.embedFail, timestamp=datetime.datetime.now())
                    
                    return await response(embed=embed, ephemeral=True)
                if isinstance(error.original, helper.errors.MildErr):
                    embed = discord.Embed(title=msgMild, description=f"{error.original}", colour=var.embedFail)
                    return await response(embed=embed, ephemeral=True)
                
                if isinstance(error.original, helper.errors.CooldownError):
                    embed = discord.Embed(title="You're on cooldown!", description=f"{error.original}", colour=var.embedFail)
                    return await response(embed=embed, ephemeral=True)
            
            if not var.production:
                raise error 
            
            print(f"{textformat.color.red}{error.__class__.__name__}{textformat.color.end} + {error}")
            embed = discord.Embed(title=msgUnkown, description=f"```{error}```\n\nJoin the [Support Server]({var.server}) for support.", colour=var.embedFail, timestamp=datetime.datetime.now())
            await response(embed=embed, ephemeral=True)
            await self.bot.get_channel(927926604838109215).send(f"> Error in **{interaction.guild.name if interaction.guild else '.'}** from **{interaction.user}**: `{error}`")
    
    async def getCommandFromError(self, error):
        commands = str(error).replace('Command "', '')
        commands = commands.replace('" is not found', '')

        return commands

async def setup(bot):
    
    await bot.add_cog(Handling1(bot))