from discord.ext import commands 
import discord

import random, os, json, time, asyncio
from setup import var
from functions import customerror
from functions import functions
import resources.commands

from discord import app_commands

import inspect

start_time = time.time()
starttime2 = time.ctime(int(time.time()))

async def help_autocomplete(ctx : discord.Interaction, current : str):
    cmds = []
    for category, commandNames in resources.commands.json.items():
        for commandName in commandNames:
            if current and current in commandName.lower():
                cmds.append(app_commands.Choice(name=commandName.title(), value=commandName))
            elif not current:
                cmds.append(app_commands.Choice(name=commandName.title(), value=commandName))
    
    return cmds[:25]

class Information1(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Get help on the bot and it's commands")
    @app_commands.describe(command="A specific command to get help for")
    @app_commands.autocomplete(command=help_autocomplete)
    async def help(self, ctx : discord.Interaction, command : str = None):
        prefix = "/"
        if command == None:
            embed = discord.Embed(
                title=random.choice(["Bot commands", "Bot help", "All bot commands"]),
                description=f"Use **{prefix}help [command]** to get help on a specific command.",
                colour=var.embed
            )
            for section in resources.commands.json:
                embed.add_field(name=section.capitalize(), value="`" + "`, `".join(resources.commands.json[section]) + "`", inline=False)
            return await ctx.response.send_message(embed=embed)
        else:
            found = False
            data = resources.commands.json
            cmdCategory = "_ _"

            tree : app_commands.CommandTree = self.bot.tree
            if var.production:
                commands = tree.walk_commands()
            else:
                commands = tree.walk_commands(guild=var.guilds[0])

            for cmd in commands:
                if cmd.name.lower() == command.lower().replace(prefix, ""):
                    if cmd.name.lower() == command.lower().replace(prefix, ""):
                        found = True
                        
                    for category in data:
                        if cmd.name == command.replace(prefix, ""):
                            if command.lower() in data[category]:
                                found = True
                        else:
                            found = True
                        
                        if cmd.name.lower() in data[category]:
                            cmdCategory = category.title()
                    
                    if found == True:
                        embed = discord.Embed(
                            title=f"Help for {prefix}{cmd.name}",
                            description=f"*{prefix}{cmd.name}* - {cmd.description}",
                            colour=var.embed
                        )

                        optionString = ""
                        for option_name, option in cmd._params.items():
                            optionString += (" *[" if option.required == False else " [") + f"{option_name}" + "]"

                        embed.add_field(name="Category", value=cmdCategory, inline=False)
                        embed.add_field(name="Description", value=cmd.description, inline=False)
                        embed.add_field(name="Usage", value=prefix + cmd.name + optionString, inline=False)
                        try:
                            embed.add_field(name="Aliases", value="`" + "`, `".join(cmd.aliases) + "`", inline=False)
                        except Exception as e:
                            pass
                        return await ctx.response.send_message(embed=embed)
            
            if not found:
                raise customerror.MildErr(f"Could not find a command with search '{command}'")
    
    @app_commands.command(name="botinfo", description="Fetches information on the bot")
    async def botinfo(self, ctx : discord.Interaction):
        second = time.time() - start_time
        minute, second = divmod(second, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)

        embed = discord.Embed(
            title=random.choice(["Bot Info", "Bot information", "Information on Helper Bot"]),
            description="Helper bot is a discord bot rewritten in early 2021 by `Coolo2#5499`. " 
            + "It has had many older versions from late 2018 to 2021."
            + f" Currently in {len(self.bot.guilds)} servers, Helper is gradually growing in popularity and commands.",
            colour=var.embed
        )
        embed.add_field(name="Server prefix", value=functions.prefix(ctx.guild), inline=False)
        embed.add_field(name="Server count", value=len(self.bot.guilds), inline=False)
        embed.add_field(name="User count", value=functions.get_bot_users(self.bot), inline=False)
        embed.add_field(name="Uptime", value="%dd %dh %dm %ds"% (day, hour, minute, second), inline=False)
        embed.add_field(name="Links", value=f"[Invite]({var.invite}) | [Support server]({var.server}) | [Vote]({var.topgg}/vote/) | [Website]({var.website})", inline=False)
        
        return await ctx.response.send_message(embed=embed)
    
    @app_commands.command(name="ping", description="Fetches the bot's response latency")
    async def ping(self, ctx : discord.Interaction):
        t1 = time.perf_counter()
        await ctx.response.defer()
        t2 = time.perf_counter()
        ping = round((t2-t1)*1000)
        pingme = str(ping)
        embed = discord.Embed(title=random.choice([":ping_pong: Pong!", "Pong!", "Responded!"]), 
            description="Bot: `" + pingme + "`" + " ms\nDiscord: `{}`ms".format(round(self.bot.latency*1000)), 
            colour=var.embed
        )
        
        await ctx.followup.send(embed=embed)
    
    async def link_command(self, ctx : discord.Interaction, m=""):
        embed = discord.Embed(title=random.choice(["My links", "My web links", "Bot links", "Check them out!"]), 
        description=f"""
        {'**' if 'invite' in m else ''}[Invite]({var.invite}){'** <--' if 'invite' in m else ''} 
        {'**' if 'support' in m or 'server' in m else ''}[Support server]({var.server}){'** <--' if 'support' in m or 'server' in m else ''} 
        {'**' if 'vote' in m or 'dbl' in m else ''}[Vote]({var.topgg}/vote){'** <--' if 'vote' in m or 'dbl' in m else ''} 
        {'**' if 'website' in m or 'page' in m else ''}[Website]({var.website}){'** <--' if 'website' in m or 'page' in m else ''}
        {'**' if 'dashboard' in m or 'setup' in m else ''}[Dashboard]({var.website}/dashboard/{(str(ctx.guild.id)) if ctx.guild else ''}){'** <--' if 'dashboard' in m or 'setup' in m else ''}
    """, color=var.embed)
        await ctx.response.send_message(embed=embed)

    @app_commands.command(name="links", description="Get bot links")
    async def links(self, ctx):
        await self.link_command(ctx)
    
    @app_commands.command(name="website", description="Get bot links")
    async def website(self, ctx):
        await self.link_command(ctx, "website")
    
    @app_commands.command(name="dashboard", description="Get bot links")
    async def dashboard(self, ctx):
        await self.link_command(ctx, "dashboard")
    
    @app_commands.command(name="support", description="Get bot links")
    async def support(self, ctx):
        await self.link_command(ctx, "support")
    
    @app_commands.command(name="vote", description="Get bot links")
    async def vote(self, ctx):
        await self.link_command(ctx, "vote")
    
    @app_commands.command(name="invite", description="Get bot links")
    async def invite(self, ctx):
        await self.link_command(ctx, "invite")
        
    
    @app_commands.command(name="randomcommand", description="Get a random bot command")
    @app_commands.describe(section="Command section to get a random command from")
    @app_commands.choices(section=[app_commands.Choice(name=x, value=x) for x in resources.commands.json])
    async def randomcommand(self, ctx : discord.Interaction, section : str = None):
        data = resources.commands.json
        
        if section != None and section.lower() in data:
            data = data[section.lower()]
            choice = random.choice(list(data))
        else:
            section = None
            choice = random.choice(list(data[random.choice(list(data))]))

        return await ctx.response.send_message(f"> Random {f'`{section}` ' if section != None else ''}command: `{functions.prefix(ctx.guild)}{choice}`")
    
    @app_commands.command(name="uptime", description="Gets the bot uptime")
    async def uptime(self, ctx : discord.Interaction):
        second = time.time() - start_time
        minute, second = divmod(second, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)
        embed = discord.Embed(title="Uptime", description="%dd %dh %dm %ds"% (day, hour, minute, second), color=var.embed)
        embed.set_footer(text="The uptime is the time since the bot was last restarted")
        await ctx.response.send_message(embed=embed)
    
    @app_commands.command(name="changelog", description="Gets the bot changelog for the current version")
    async def changelog(self, ctx : discord.Interaction):
        embed = discord.Embed(title=f"Changelog for version {var.version}", description=f"View the changelog on [the website]({var.address}/changelogs)", color=var.embed)

        await ctx.response.send_message(embed=embed)



async def setup(bot):
    await bot.add_cog(Information1(bot), guilds=var.guilds)