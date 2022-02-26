from discord.ext import commands 
import discord

from discord.commands import slash_command, Option

import random, os, json
from functions import customerror, functions, google
from setup import var
from datetime import datetime, timedelta
import wikipedia
from EasyConversion import convert, info
from googletrans import Translator
import asyncio, re

class Utility1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="poll", description="Make a poll")
    async def poll(self, ctx, question : Option(str, "The question to ask")):
        embed = discord.Embed(color=var.embed)
        embed.add_field(name="Poll from {}".format(ctx.author), value= question)
        reactthis = await ctx.respond(embed=embed)

        msg = await (reactthis).original_message()

        await msg.add_reaction("✅")
        await msg.add_reaction("<:red_cross:858621367053975562>")
    
    @slash_command(name="randomnumber", description="Get a random number", aliases=["random-number"])
    async def randomnumber(
        self, 
        ctx, 
        bottomNumber : Option(int, required=False, name="minimum-number", description="The minimum number to choose from") = None, 
        topNumber : Option(int, required=False, name="maximum-number", description="The maximum number to choose from") = None
    ):
        if bottomNumber != None:
            if topNumber != None:
                embed = discord.Embed(title="Random number from {} to {}".format(bottomNumber, topNumber), colour=var.embed, description=random.randint(int(bottomNumber), int(topNumber)))
            if topNumber == None:
                embed = discord.Embed(title="Random number from 1 to {}".format(bottomNumber), colour=var.embed, description=random.randint(1, int(bottomNumber)))
        if bottomNumber == None:
            embed = discord.Embed(title="Random number", colour=var.embed, description=f"""
Random number from **1** to **10:** {random.randint(1, 10)}
Random number from **1** to **100:** {random.randint(1, 100)}
Random number from **1** to **1000:** {random.randint(1, 1000)}
Random number from **1** to **1,000,000**: {random.randint(1, 1000000)}""")
        await ctx.respond(embed=embed)
    
    @slash_command(name="google", description="Search google", aliases=["search", "googlesearch", "google-search"])
    async def google(self, ctx, query : Option(str, name="query", description="The query to search google for")):
        search = await google.search(query, num_results=10)

        embed = discord.Embed(title=f"Results for: {query}", color=var.embed)

        for result in search[:-1]:
            viewURL = ('.'.join(result.url.split('.')[1:]) if 'www.' in result.url else '/'.join(result.url.split('/')[2:]))[0:30] + "..."
            embed.add_field(name=result.title, value=f"[{viewURL}]({result.url}) - {result.description}", inline=False)
        
        await ctx.respond(embed=embed)
    
    @slash_command(name="hyperlink", description="Make a hyperlink")
    async def hyperlink(
        self, 
        ctx, 
        url : Option(str, description="The URL to link to"), 
        message : Option(str, description="The message to go infront of the URL")
    ):
        
        if "http" not in url:
            url = "http://" + url + "/"
        try:
            em = discord.Embed(title=message, url=url, colour=var.embed)
            await ctx.respond(embed=em)
        except Exception as e:
            await ctx.respond("> Could not find a valid URL.")
    
    @slash_command(name="wikipedia", description="Search wikipedia for an article")
    async def wikipedia(self, ctx, query : Option(str, description="Query to search on wikipedia")):
        try:
            summary = wikipedia.summary(query, sentences=5, auto_suggest=False)
        except Exception as e:
            summary = "Could not find article! Did you mean: \n`" + ("`, `".join(str(e).split("\n")[1:20])) + "`"

        embed = discord.Embed(title=f"Here is a wikipedia article for {query}.", description=summary, colour=var.embed)
        await ctx.respond(embed=embed)
    
    @slash_command(name="userinfo", description="Check info for a user", aliases=['memberinfo'])
    async def userinfo(self, ctx, user: Option(discord.User, description="The user to get info for")):
        if user == None:
            user = ctx.author
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
        await ctx.respond(embed=embed)
    
    @slash_command(name="serverinfo", description="Get info on the server", aliases=['guildinfo', 'server-info', 'guild-info'])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        embed = discord.Embed(title="Information For " + ctx.guild.name, color=var.embed)
        embed.add_field(name="Server Name", value= ctx.guild.name)
        embed.add_field(name="Server ID", value= ctx.guild.id)
        embed.add_field(name="Server Creation Date", value= f"<t:{int(ctx.guild.created_at.timestamp())}:F> (<t:{int(ctx.guild.created_at.timestamp())}:R>)")
        embed.add_field(name="Preferred Locale", value= ctx.guild.preferred_locale)
        embed.add_field(name="Verification level", value= str(ctx.guild.verification_level))
        embed.add_field(name="Owner", value= ctx.guild.owner.mention)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.set_footer(text=f"See more info with {functions.prefix(ctx.guild)}serverstats")
        
        await ctx.respond(embed=embed)
    
    @slash_command(name="serverstatistics", description="Get stats for the server", aliases=['serverstats', 'srvrstats', 'server-stats', 'server-statistics'])
    @commands.guild_only()
    async def serverstatistics(self, ctx):
        embed = discord.Embed(title="{}'s Server statistics".format(ctx.guild.name), color=var.embed)
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else None)
        embed.add_field(name="Members", value=len(ctx.guild.members))
        embed.add_field(name="Bots", value=str(sum(member.bot for member in ctx.guild.members)))
        embed.add_field(name="Administrators", value=str(sum(member.guild_permissions.administrator and not member.bot for member in ctx.guild.members)))
        embed.add_field(name="Roles", value=len(ctx.guild.roles))
        embed.add_field(name="Channels", value=len(ctx.guild.channels))
        embed.add_field(name="Age", value=f"{(datetime.now() - ctx.guild.created_at.replace(tzinfo=None)).days} days")
        embed.set_footer(text=f"See more info with {functions.prefix(ctx.guild)}serverinfo")

        await ctx.respond(embed=embed)
    
    @slash_command(name="convert", description="Convert from morse or binary to text (and vice versa)", aliases=['convert-from', 'convertfrom', 'converter'])
    async def convert(
        self, 
        ctx, 
        convertType : Option(str, name="convert-type", choices=["morse", "binary"], description="What to convert to"), 
        convertInput : Option(str, name="input", description="THe input to be converted")
    ):
        if convertType.lower() not in ["morse", "morsecode", "morse-code"] + ["ascii", "binary"]:
            raise customerror.CustomErr(f"Invalid convert type! Please use {functions.prefix(ctx.guild)}convert [ascii/morse] [input to convert]")

        embed = discord.Embed(
            title="Converted successfully!", 
            description=
                "```" + 
                (convert.detect.morsestring(convertType) if convertType.lower() in ["morse", "morsecode", "morse-code"] else convert.detect.asciistring(convertInput, return_type=str) if convertType.lower() in ["ascii", "binary"] else "_ _") + 
                f"```\nConvert it back with `{functions.prefix(ctx.guild)}convert {convertType} [input]`", 
            color=var.embed
        )
        embed.set_footer(text="Command made with EasyConversion {} | tiny.cc/EasyConversion".format(info.version.current.name))
        try:
            await ctx.respond(embed=embed)
        except Exception as e:
            await ctx.respond("> Output too long!")
    
    @slash_command(name="avatar", description="Get a user's profile picture", aliases=['pfp', 'logo', 'profilepicture', 'useravatar'])
    async def avatar(self, ctx, user : Option(discord.User, description="User to get the avatar of")):
        if user == None:
            user = ctx.author
        embed = discord.Embed(title="{}'s avatar".format(user.display_name), color=var.embed)
        embed.set_image(url=user.avatar.url if user.avatar else None)
        await ctx.respond(embed=embed)
    


    @slash_command(name="remind", description="Send a message in a certain amount of time", aliases = ['reminder', 'remindme'])
    async def remind(
        self, 
        ctx, 
        time : Option(str, description="The time to wait to remind you in"), 
        reminder : Option(str, description="The text to remind you with", required=False) = None
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
            raise customerror.MildErr("Invalid time! Time must be a number above 1.")

        await ctx.respond("> I will remind you in " + str(amount) + " second(s)", ephemeral=True)

        await asyncio.sleep(int(amount))
        await ctx.send(content=ctx.author.mention, embed=
            discord.Embed(
                title=f"Reminder from {ctx.author}",
                description=reminder,
                color=var.embed
            )
        )
    
    @slash_command(name="timer", description="Create a timer")
    async def timer(self, ctx, time : Option(str, description="The time to wait to finish")):
        try:
            if " " in time:

                time1 = time.split(" ")[0]
                time2 = time.split(" ")[1]

                if True in [c in str(time) for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV1234567890!@#$%^&*()=+;'\[]:"]:
                    amount = int(functions.calculateTime(time1)) + int(functions.calculateTime(time2))
            else:
                amount = int(functions.calculateTime(time))
                
        except Exception as e:
            raise customerror.MildErr("Invalid time! Time must be a number above 1.")
        
        if amount < 1:
            raise customerror.MildErr("Invalid time! Time must be a number above 1.")

        await ctx.respond("> Started timer for " + str(amount) + " seconds", ephemeral=True)
        await asyncio.sleep(amount)
        await ctx.channel.send(f"> Timer for `{amount}` seconds from {ctx.author.mention} ended.", allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
    

        
def setup(bot):
    bot.add_cog(Utility1(bot))