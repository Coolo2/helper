from discord.ext import commands 
import discord

import random, os, time, json
from setup import var
from functions import functions, paginator
import resources.commands
import helper

from discord import app_commands

start_time = time.time()
starttime2 = time.ctime(int(time.time()))



class Information1(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
    
    bot = app_commands.Group(name="bot", description="Bot information commands")

    @bot.command(name="help", description="Get help on the bot and its commands")
    @app_commands.describe(_command="A specific command to get help for")
    @app_commands.autocomplete(_command=helper.autocompletes.commands_autocomplete)
    @app_commands.rename(_command="command")
    async def _help(self, interaction : discord.Interaction, _command : str = None):

        with open("databases/commands.json") as f:
            customCommands = json.load(f)

        if _command:
            _command = _command.replace("/", "")
            command_split = [_command] if " " not in _command else _command.split(" ")

            command = None
            for item in command_split:
                if not command:
                    command = self.bot.tree.get_command(item)
                else:
                    command = command.get_command(item)
            
            if not command or type(command) == app_commands.Group or command.extras.get("IGNORE_IN_COMMAND_LISTS"):
                raise helper.errors.MildErr(
                    f"Command not found with name `{_command}`!" + (
                        " You cannot get extra help for custom commands." if str(interaction.guild.id) in customCommands and _command in customCommands[str(interaction.guild.id)] else ""
                    )
                )

            embed = helper.styling.MainEmbed(f"Help for /{command.qualified_name}", f"*/{command.qualified_name}* - {command.description}")

            optionString = ""
            for option_name, option in command._params.items():
                optionString += (" \*[" if option.required == False else " [") + f"{option_name}" + "]"

            embed.add_field(name="Category", value=helper.utils.category_name_from_cog_name(command.module).title(), inline=False)
            embed.add_field(name="Usage", value="/" + command.qualified_name + optionString, inline=False)

            return await interaction.response.send_message(embed=embed)
        
        embed = helper.styling.MainEmbed("Bot help", "Use **/bot help [command]** to get help on a specific command.")
        categories : dict[str, list] = {}

        for command in self.bot.tree.walk_commands():
            if command.extras.get("IGNORE_IN_COMMAND_LISTS"): continue

            category_name = helper.utils.category_name_from_cog_name(command.module)
    
            if category_name not in categories:
                categories[category_name] = []
            
            categories[category_name].append(command.qualified_name)

        for category_name, commands in categories.items():
            if len(commands) > 0:
                embed.add_field(name=category_name.title(), value="`/" + ("`, `/".join(commands)) + "`", inline=False)
        
        if str(interaction.guild.id) in customCommands and len(customCommands[str(interaction.guild.id)]) > 0:
            embed.add_field(name="Custom commands", value="`/" + ("`, `/".join(customCommands[str(interaction.guild.id)])) + "`")
        
        return await interaction.response.send_message(embed=embed)
    
    @bot.command(name="info", description="Fetches information on the bot")
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
        embed.add_field(name="Server count", value=len(self.bot.guilds), inline=False)
        embed.add_field(name="User count", value=functions.get_bot_users(self.bot), inline=False)
        embed.add_field(name="Uptime", value="%dd %dh %dm %ds"% (day, hour, minute, second), inline=False)
        embed.add_field(name="Links", value=f"[Invite]({var.invite}) | [Support server]({var.server}) | [Vote]({var.topgg}/vote/) | [Website]({var.address})", inline=False)
        
        return await ctx.response.send_message(embed=embed)
    
    @bot.command(name="ping", description="Fetches the bot's response latency")
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
    

    @bot.command(name="links", description="Get bot links")
    async def links(self, ctx : discord.Interaction):
        embed = discord.Embed(title=random.choice(["My links", "My web links", "Bot links", "Check them out!"]), 
            description=f"""
[Invite]({var.invite})
[Support server]({var.server})
[Vote]({var.topgg}/vote)
[Website]({var.address})
[Dashboard]({var.address}/dashboard/{(str(ctx.guild.id)) if ctx.guild else ''})
            """, color=var.embed)
        await ctx.response.send_message(embed=embed)

        
    
    @bot.command(name="randomcommand", description="Get a random bot command")
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
        
        embed = discord.Embed(title="Here's your random command!", description=f"/{choice}", color=var.embed)

        return await ctx.response.send_message(embed=embed)
    
    @bot.command(name="changelogs", description="Get a history of the bot")
    async def _changelogs(self, interaction : discord.Interaction):
        changelogs = []
        for file in [f for f in os.listdir("./resources/changelogs/") if os.path.isfile(os.path.join("./resources/changelogs/", f))]:
            with open("resources/changelogs/" + file) as f:
                changelog = f.read()
                split = changelog.split("\n")
                split[0] = "# " + split[0] 
                changelog = "\n".join(split)
                changelog = changelog.replace("\n<u>", "### ").replace("</u>", "")

                changelogs.append(functions.format_html_basic(changelog))
        
        embed = discord.Embed(title=f"Changelogs up to {var.version}", color=var.embed)
        p = paginator.PaginatorView(embed, "newchangelog".join(changelogs), "newchangelog", 1, -1, search=False, private=interaction.user)

        return await interaction.response.send_message(embed=p.embed, view=p)




async def setup(bot):
    await bot.add_cog(Information1(bot))