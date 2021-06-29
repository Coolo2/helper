import discord, random, os, json, time, asyncio
from discord.ext import commands
from setup import var
from functions import customerror
from functions import functions
import resources.commands

start_time = time.time()
starttime2 = time.ctime(int(time.time()))

class Information1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help", description="*[command]|Get help on the bot and it's commands", aliases=['cmds', 'commands', 'hlp', 'botcommands', 'bot-commands'])
    async def help(self, ctx, command = None):
        prefix = functions.prefix(ctx.guild) 
        if command == None:
            embed = discord.Embed(
                title=random.choice(["Bot commands", "Bot help", "All bot commands"]),
                description=f"Use **{prefix}help [command]** to get help on a specific command.",
                colour=var.embed
            )
            for section in resources.commands.json:
                embed.add_field(name=section.capitalize(), value="`" + "`, `".join(resources.commands.json[section]) + "`", inline=False)
            return await ctx.send(embed=embed)
        else:
            found = False
            data = resources.commands.json
            cmdCategory = "_ _"

            for cmd in self.bot.commands:
                if cmd.name.lower() == command.lower().replace(prefix, "") or command in cmd.aliases:
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
                            description=f"*{prefix}{cmd.name}* - {cmd.description.split('|')[1]}",
                            colour=var.embed
                        )
                        embed.add_field(name="Category", value=cmdCategory, inline=False)
                        embed.add_field(name="Description", value=cmd.description.split('|')[1], inline=False)
                        embed.add_field(name="Usage", value=prefix + cmd.name + " " + cmd.description.split("|")[0], inline=False)
                        try:
                            embed.add_field(name="Aliases", value="`" + "`, `".join(cmd.aliases) + "`", inline=False)
                        except:
                            pass
                        return await ctx.send(embed=embed)
            
            if not found:
                raise customerror.MildErr(f"Could not find a command with search '{command}'")
    
    @commands.command(name="botinfo", description="|Fetches information on the bot", aliases = ['info', 'about'])
    async def botinfo(self, ctx):
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
        
        return await ctx.send(embed=embed)
    
    @commands.command(name="ping", description="|Fetches the bot's response latency", aliases=["getping"])
    async def ping(self, ctx):
        t1 = time.perf_counter()
        message = await ctx.send("Pinging...")
        t2 = time.perf_counter()
        ping = round((t2-t1)*1000)
        pingme = str(ping)
        embed = discord.Embed(title=random.choice([":ping_pong: Pong!", "Pong!", "Responded!"]), 
            description="Bot: `" + pingme + "`" + " ms\nDiscord: `{}`ms".format(round(self.bot.latency*1000)), 
            colour=var.embed
        )
        await message.edit(embed=embed)
    
    @commands.command(name="links", description="|Get bot links", aliases=["website", "page", "dashboard", "botlinks", "invite", "vote", "support", "server", "supportserver"])
    async def links(self, ctx):
        m = str(ctx.message.content)
        embed = discord.Embed(title=random.choice(["My links", "My web links", "Bot links", "Check them out!"]), 
        description=f"""
        {'**' if 'invite' in m else ''}[Invite]({var.invite}){'** <--' if 'invite' in m else ''} 
        {'**' if 'support' in m or 'server' in m else ''}[Support server]({var.server}){'** <--' if 'support' in m or 'server' in m else ''} 
        {'**' if 'vote' in m or 'dbl' in m else ''}[Vote]({var.topgg}/vote){'** <--' if 'vote' in m or 'dbl' in m else ''} 
        {'**' if 'website' in m or 'page' in m else ''}[Website]({var.website}){'** <--' if 'website' in m or 'page' in m else ''}
        {'**' if 'dashboard' in m or 'setup' in m else ''}[Dashboard]({var.website}/dashboard/{ctx.guild.id}){'** <--' if 'dashboard' in m or 'setup' in m else ''}
    """, color=var.embed)
        await ctx.send(embed=embed)
    
    @commands.command(name="randomcommand", description="*[section]|Get a random bot command", aliases=["random-command", "random-cmd", "randomcmd"])
    async def randomcommand(self, ctx, section=None):
        data = resources.commands.json
        
        if section != None and section.lower() in data:
            data = data[section.lower()]
            choice = random.choice(list(data))
        else:
            section = None
            choice = random.choice(list(data[random.choice(list(data))]))

        return await ctx.send(f"> Random {f'`{section}` ' if section != None else ''}command: `{functions.prefix(ctx.guild)}{choice}`")
    
    @commands.command(name="uptime", description="|Gets the bot uptime", aliases=["up-time", "up"])
    async def uptime(self, ctx):
        second = time.time() - start_time
        minute, second = divmod(second, 60)
        hour, minute = divmod(minute, 60)
        day, hour = divmod(hour, 24)
        embed = discord.Embed(title="Uptime", description="%dd %dh %dm %ds"% (day, hour, minute, second), color=var.embed)
        embed.set_footer(text="The uptime is the time since the bot was last restarted")
        await ctx.send(embed=embed)
    
    @commands.command(name="changelog", description="|Gets the bot changelog for the current version", aliases=["changelogs", "change-log", "change-logs"])
    @commands.guild_only()
    async def changelog(self, ctx):
        prefix = functions.prefix(ctx.guild)
        changelog = functions.changelog()
        changelog = changelog.replace("{prefix}", prefix).replace("{websitelink}", var.website)
        
        if ctx.message.guild.me.guild_permissions.external_emojis and ctx.message.guild.me.guild_permissions.add_reactions:
            if len(changelog) < 1024:  

                embed = discord.Embed(title=f"Changelog for version {var.version}\n Click <:script:716964697223725123> to show development changes!", description=changelog.split("__Development changes:__")[0], color=var.embed)

                embeds = discord.Embed(title=f"Changelog for version {var.version}\n Click <:script:716964697223725123> to hide development changes!", 
                    description=changelog.split("__Development changes:__")[0] + "__Development changes:__" + changelog.split("__Development changes:__")[1], color=var.embed)
                msg = await ctx.send(embed=embed)

                embed2 = discord.Embed(title=f"Changelog for version {var.version}", description=changelog.split("__Development changes:__")[0], color=var.embed)

            else:

                preembed = discord.Embed(title=f"Changelog for version {var.version}\n Click <:script:716964697223725123> to show development changes!", 
                    description=changelog.split("__Development changes:__")[0].split("__Bug fixes:__")[0], color=var.embed)

                embed = discord.Embed(title=f"Changelog for version {var.version}\n Click <:script:716964697223725123> to show development changes!", 
                    description="__Bug fixes:__" + changelog.split("__Development changes:__")[0].split("__Bug fixes:__")[1], color=var.embed)

                embeds = discord.Embed(title=f"Changelog for version {var.version}\n Click <:script:716964697223725123> to hide development changes!", 
                    description=changelog.split("__Development changes:__")[0].split("__Bug fixes:__")[1] + "__Development changes:__" + changelog.split("__Development changes:__")[1], color=var.embed)

                await ctx.send(embed=preembed)
                msg = await ctx.send(embed=embed)

                embed2 = discord.Embed(title=f"Changelog for version {var.version}", 
                    description="__Bug fixes:__" + changelog.split("__Development changes:__")[0].split("__Bug fixes:__")[1], color=var.embed)

            await msg.add_reaction("<:script:716964697223725123>")

            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) == '<:script:716964697223725123>'

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                pass
            else:
                await msg.edit(embed=embeds)
            try:
                reaction, user = await self.bot.wait_for('reaction_remove', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                pass
            else:
                await msg.edit(embed=embed2)
                try:
                    await msg.clear_reactions()
                except:
                    pass
        else:
            embed2 = discord.Embed(title=f"Changelog for version {var.version}", color=var.embed)
            embed2.add_field(name="Changelog:", value=changelog.split("__Development changes:__")[0])
            await ctx.send(embed=embed2)


def setup(bot):
    bot.add_cog(Information1(bot))