from discord.ext import commands 
import discord

import random
from functions import functions, google
from setup import var
from datetime import datetime
from EasyConversion import convert, info
import asyncio

from discord import app_commands

from wikipya import Wikipya
from wikipya.exceptions import NotFound
import helper

class Utility1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.wiki = Wikipya(lang="en").get_instance()

    @app_commands.command(name="poll", description="Make a poll")
    @app_commands.describe(question="The question to ask")
    async def poll(self, ctx : discord.Interaction, question : str):
        embed = discord.Embed(color=var.embed)
        embed.add_field(name="Poll from {}".format(ctx.user), value= question)
        reactthis = await ctx.response.send_message(embed=embed)
        msg = await ctx.original_response()

        await msg.add_reaction("✅")
        await msg.add_reaction("<:red_cross:858621367053975562>")
    
    @app_commands.command(name="randomnumber", description="Get a random number")
    @app_commands.describe(minimum_number="The minimum number to choose from", maximum_number="The maximum number to choose from")
    async def randomnumber(
        self, 
        ctx, 
        minimum_number : int = None, 
        maximum_number : int = None
    ):
        if minimum_number != None:
            if maximum_number != None:
                embed = discord.Embed(title="Random number from {} to {}".format(minimum_number, maximum_number), colour=var.embed, description=random.randint(int(minimum_number), int(maximum_number)))
            if maximum_number == None:
                embed = discord.Embed(title="Random number from 1 to {}".format(minimum_number), colour=var.embed, description=random.randint(1, int(minimum_number)))
        if minimum_number == None:
            embed = discord.Embed(title="Random number", colour=var.embed, description=f"""
Random number from **1** to **10:** {random.randint(1, 10)}
Random number from **1** to **100:** {random.randint(1, 100)}
Random number from **1** to **1000:** {random.randint(1, 1000)}
Random number from **1** to **1,000,000**: {random.randint(1, 1000000)}""")
        await ctx.response.send_message(embed=embed)
    
    @app_commands.command(name="google", description="Search google")
    @app_commands.describe(query="The query to search google for")
    async def google(self, ctx, query : str):
        search = await google.search(query, num_results=10)

        embed = discord.Embed(title=f"Results for: {query}", color=var.embed)

        for result in search[:-1]:
            viewURL = ('.'.join(result.url.split('.')[1:]) if 'www.' in result.url else '/'.join(result.url.split('/')[2:]))[0:30] + "..."
            embed.add_field(name=result.title, value=f"[{viewURL}]({result.url}) - {result.description}", inline=False)
        
        await ctx.response.send_message(embed=embed)
    
    @app_commands.command(name="hyperlink", description="Make a hyperlink")
    @app_commands.describe(url="The URL to link to", message="The message to hyperlink")
    async def hyperlink(
        self, 
        ctx, 
        url : str, 
        message : str
    ):
        
        if "http" not in url:
            url = "http://" + url + "/"
        try:
            em = discord.Embed(title=message, url=url, colour=var.embed)
            await ctx.response.send_message(embed=em)
        except Exception as e:
            await ctx.response.send_message("> Could not find a valid URL.")
    
    @app_commands.command(name="wikipedia", description="Search wikipedia for an article")
    @app_commands.describe(query="The query to search wikipedia for")
    async def wikipedia(self, ctx, query : str):
        
        try:
            search = await self.wiki.search(query)
        except NotFound:
            raise helper.errors.MildErr("Couldn't find any results for this query!")

        page = await self.wiki.page(search[0].page_id)
        
        parsed = functions.format_html_basic(page.parsed)[:4095]

        embed = discord.Embed(title=f"Here is a wikipedia article for {query}.", description=parsed, colour=var.embed)
        embed.add_field(name="Read more", value=f"https://en.wikipedia.org/wiki/{page.title.replace(' ', '_')}")
        await ctx.response.send_message(embed=embed)
    
    @wikipedia.autocomplete("query")
    async def _autocomplete(self, interaction : discord.Interaction, namespace : str):
        pages = []
        if namespace:
            try:
                pages = await self.wiki.search(namespace, limit=25)
            except NotFound:
                pass

        return [app_commands.Choice(name=p.title, value=p.title) for p in pages]
    
    @app_commands.command(name="userinfo", description="Check info for a user")
    @app_commands.describe(user="The user to get info for")
    async def userinfo(self, ctx, user: discord.User):
        if user == None:
            user = ctx.user
        member = ctx.guild.get_member(user.id)
        embed = discord.Embed(title ="Information For " + str(user), color=var.embed)
        embed.add_field(name="Username", value=user.name)
        embed.add_field(name="User ID", value=user.id)
        embed.add_field(name="User Creation Date", value=f"<t:{int(user.created_at.timestamp())}:F> (<t:{int(user.created_at.timestamp())}:R>)")
        if member != None:
            embed.add_field(name="User Join Date", value=f"<t:{int(member.joined_at.timestamp())}:F> (<t:{int(member.joined_at.timestamp())}:R>)")
            embed.add_field(name="Color", value=member.color)
            embed.add_field(name="Users Highest Role", value=member.top_role.mention)
        else:
            embed.set_footer(text="This user is from another server.")
        embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
        await ctx.response.send_message(embed=embed)
    
    @app_commands.command(name="serverinfo", description="Get info on the server")
    @app_commands.guild_only()
    async def serverinfo(self, ctx):
        embed = discord.Embed(title="Information For " + ctx.guild.name, color=var.embed)
        embed.add_field(name="Server Name", value= ctx.guild.name)
        embed.add_field(name="Server ID", value= ctx.guild.id)
        embed.add_field(name="Server Creation Date", value= f"<t:{int(ctx.guild.created_at.timestamp())}:F> (<t:{int(ctx.guild.created_at.timestamp())}:R>)")
        embed.add_field(name="Preferred Locale", value= ctx.guild.preferred_locale)
        embed.add_field(name="Verification level", value= str(ctx.guild.verification_level))
        embed.add_field(name="Owner", value= ctx.guild.owner.mention)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"See more info with /serverstats")
        
        await ctx.response.send_message(embed=embed)
    
    @app_commands.command(name="serverstatistics", description="Get stats for the server")
    @app_commands.guild_only()
    async def serverstatistics(self, ctx):
        embed = discord.Embed(title="{}'s Server statistics".format(ctx.guild.name), color=var.embed)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.add_field(name="Members", value=len(ctx.guild.members))
        embed.add_field(name="Bots", value=str(sum(member.bot for member in ctx.guild.members)))
        embed.add_field(name="Administrators", value=str(sum(member.guild_permissions.administrator and not member.bot for member in ctx.guild.members)))
        embed.add_field(name="Roles", value=len(ctx.guild.roles))
        embed.add_field(name="Channels", value=len(ctx.guild.channels))
        embed.add_field(name="Age", value=f"{(datetime.now() - ctx.guild.created_at.replace(tzinfo=None)).days} days")
        embed.set_footer(text=f"See more info with /serverinfo")

        await ctx.response.send_message(embed=embed)
    
    @app_commands.command(name="convert", description="Convert from morse or binary to text (and vice versa)")
    @app_commands.describe(convert_type="The type of conversion", text="The text to convert")
    @app_commands.choices(convert_type=[app_commands.Choice(name="Morse", value="morse"), app_commands.Choice(name="Binary", value="binary")])
    async def convert(
        self, 
        ctx, 
        convert_type : str, 
        text : str
    ):
        if convert_type.lower() not in ["morse", "morsecode", "morse-code"] + ["ascii", "binary"]:
            raise helper.errors.CustomErr(f"Invalid convert type! Please use /convert [ascii/morse] [input to convert]")

        embed = discord.Embed(
            title="Converted successfully!", 
            description=
                "```" + 
                (convert.detect.morsestring(convert_type) if convert_type.lower() in ["morse", "morsecode", "morse-code"] else convert.detect.asciistring(text, return_type=str) if convert_type.lower() in ["ascii", "binary"] else "_ _") + 
                f"```\nConvert it back with `/convert {convert_type} [input]`", 
            color=var.embed
        )
        embed.set_footer(text="Command made with EasyConversion {} | tiny.cc/EasyConversion".format(info.version.current.name))
        try:
            await ctx.response.send_message(embed=embed)
        except Exception as e:
            await ctx.response.send_message("> Output too long!")
    
    @app_commands.command(name="avatar", description="Get a user's profile picture")
    async def avatar(self, ctx, user : discord.User):
        if user == None:
            user = ctx.user
        embed = discord.Embed(title="{}'s avatar".format(user.display_name), color=var.embed)
        embed.set_image(url=user.avatar.url if user.avatar else None)
        await ctx.response.send_message(embed=embed)
    


    @app_commands.command(name="remind", description="Send a message in a certain amount of time")
    @app_commands.describe(time="The time to wait", reminder="The reminder to send with the timer")
    async def remind(
        self, 
        ctx, 
        time : str, 
        reminder : str = None
    ):
        if reminder == None:
            reminder = "None"

        try:
            if " " in time:

                time1 = time.split(" ")[0]
                time2 = time.split(" ")[1]

                if True in [c in str(time) for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV1234567890!@#$%^&*()=+;'\[]:"]:
                    amount = int(functions.calculateTime(time1)) + int(functions.calculateTime(time2))
            else:
                amount = int(functions.calculateTime(time))
                
        except Exception as e:
            raise helper.errors.MildErr("Invalid time! Time must be a number above 1.")

        await ctx.response.send_message("> I will remind you in " + str(amount) + " second(s)", ephemeral=True)

        await asyncio.sleep(int(amount))
        await ctx.channel.send(content=ctx.user.mention, embed=
            discord.Embed(
                title=f"Reminder from {ctx.user}",
                description=reminder,
                color=var.embed
            )
        )
    
    @app_commands.command(name="timer", description="Create a timer")
    @app_commands.describe(time="The time to wait")
    async def timer(self, ctx, time : str):
        try:
            if " " in time:

                time1 = time.split(" ")[0]
                time2 = time.split(" ")[1]

                if True in [c in str(time) for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV1234567890!@#$%^&*()=+;'\[]:"]:
                    amount = int(functions.calculateTime(time1)) + int(functions.calculateTime(time2))
            else:
                amount = int(functions.calculateTime(time))
                
        except Exception as e:
            raise helper.errors.MildErr("Invalid time! Time must be a number above 1.")
        
        if amount < 1:
            raise helper.errors.MildErr("Invalid time! Time must be a number above 1.")

        await ctx.response.send_message("> Started timer for " + str(amount) + " seconds", ephemeral=True)
        await asyncio.sleep(amount)
        await ctx.channel.send(f"> Timer for `{amount}` seconds from {ctx.user.mention} ended.", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
    

        
async def setup(bot):
    await bot.add_cog(Utility1(bot))