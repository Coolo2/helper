
import discord

from discord.ext import commands
from discord.commands import errors

import random, os, json, re
from functions import customerror, functions
from setup import var
from EasyConversion import textformat

import datetime

class Handling1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        
        msgMild = random.choice(["Uh oh!", "Oops!", "Oh no!"])
        msgUnkown = random.choice(["You've ran into an unknown error!", "You've ran into an error!"])
        
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title=msgMild, description=f"```{error}\n{functions.prefix(ctx.guild)}{ctx.command.name} {ctx.command.description.split('|')[0]}```", colour=var.embedFail, timestamp=datetime.datetime.now())
            return await ctx.respond(embed=embed, ephemeral=True)
        
        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(title=msgMild, description=f"```{error}```", colour=var.embedFail, timestamp=datetime.datetime.now())
            return await ctx.respond(embed=embed, ephemeral=True)
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(title=msgMild, description=f"{error}", colour=var.embedFail)
            return await ctx.respond(embed=embed, ephemeral=True)
        if isinstance(error, commands.CommandNotFound):
            cc = await self.customCommands(ctx, error)
            similar = await self.checkCustomCommands(ctx, error)
            command = await self.getCommandFromError(error)

            if cc == False:
                if similar != False:
                    embed = discord.Embed(title=msgMild, 
                        description=f"Command **{functions.prefix(ctx.guild)}{command}** was not found! You may have meant **{functions.prefix(ctx.guild)}{similar}**.", colour=var.embedFail, timestamp=datetime.datetime.now())
                    return await ctx.respond(embed=embed, ephemeral=True)
                return await self.bot.get_user(var.owner).send(f"> Error in **{ctx.guild.name}** from **{ctx.author}**: `{error}`")
            else:
                return
        if isinstance(error, errors.CheckFailure):
            embed = discord.Embed(title=msgMild, description=f"t", colour=var.embedFail)
            return await ctx.respond(embed=embed, ephemeral=True)

        if isinstance(error, errors.ApplicationCommandInvokeError):
            if isinstance(error.original, commands.MemberNotFound):
                embed = discord.Embed(title=msgMild, description=f"```{str(error.original)}```", colour=var.embedFail, timestamp=datetime.datetime.now())
                return await ctx.respond(embed=embed, ephemeral=True)
            if isinstance(error.original, commands.MissingPermissions):
                embed = discord.Embed(title=msgMild, description=f"```{error.original}```", colour=var.embedFail, timestamp=datetime.datetime.now())
                return await ctx.respond(embed=embed, ephemeral=True)
            if isinstance(error.original, commands.BotMissingPermissions):
                embed = discord.Embed(title=msgMild, 
                description=f"```{error.original}\n\nEnsure that I have the above permissions and my role is high enough to use {functions.prefix(ctx.guild)}{ctx.command.name}```", 
                colour=var.embedFail, timestamp=datetime.datetime.now())
                return await ctx.respond(embed=embed, ephemeral=True)
            if isinstance(error.original, errors.CheckFailure):
                embed = discord.Embed(title=msgMild, description=f"t", colour=var.embedFail)
                return await ctx.respond(embed=embed, ephemeral=True)

            # Custom errors
            if isinstance(error.original, customerror.CustomErr):
                embed = discord.Embed(title=msgMild, description=f"```{error.original}```", colour=var.embedFail, timestamp=datetime.datetime.now())
                return await ctx.respond(embed=embed, ephemeral=True)
            if isinstance(error.original, customerror.MildErr):
                embed = discord.Embed(title=msgMild, description=f"{error.original}", colour=var.embedFail)
                return await ctx.respond(embed=embed, ephemeral=True)
            
            if isinstance(error.original, customerror.CooldownError):
                embed = discord.Embed(title="You're on cooldown!", description=f"{error.original}", colour=var.embedFail)
                return await ctx.respond(embed=embed, ephemeral=True)

        print(f"{textformat.color.red}{error.__class__.__name__}{textformat.color.end} + {error}")
        embed = discord.Embed(title=msgUnkown, description=f"```{error}```\n\nJoin the [Support Server]({var.server}) for support.", colour=var.embedFail, timestamp=datetime.datetime.now())
        await ctx.respond(embed=embed, ephemeral=True)
        await self.bot.get_channel(927926604838109215).send(f"> Error in **{ctx.guild.name}** from **{ctx.author}**: `{error}`")
    
    async def getCommandFromError(self, error):
        commands = str(error).replace('Command "', '')
        commands = commands.replace('" is not found', '')

        return commands
    
    async def checkCustomCommands(self, ctx, error):
        commands = await self.getCommandFromError(error)

        mainCommands = functions.checkList(self.bot.commands, commands)
        musicCommands = functions.checkList(var.musicCommands, commands)
        customCommands = None

        with open("databases/commands.json") as f:
            data = json.load(f)
        
        if str(ctx.guild.id) in data:
            customCommands = functions.checkList(list(data[str(ctx.guild.id)].keys()), commands)

        if mainCommands != None:
            return mainCommands
        if musicCommands != None:
            return musicCommands
        if customCommands != None:
            return customCommands
        
        return False

def setup(bot):
    bot.add_cog(Handling1(bot))