import discord, random, os, json
from discord.ext import commands
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

    @commands.command(name="poll", description="[question]|Make a poll")
    async def poll(self, ctx, *, question):
        embed = discord.Embed(color=var.embed)
        embed.add_field(name="Poll from {}".format(ctx.author), value= question)
        reactthis = await ctx.send(embed=embed)
        await reactthis.add_reaction("✅")
        await reactthis.add_reaction("<:red_cross:858621367053975562>")
        await ctx.message.delete()

    @commands.command(name="randomnumber", description="*[bottomNumber] *[topNumber]|Get a random number", aliases=["random-number"])
    async def randomnumber(self, ctx, bottomNumber = None, topNumber = None):
        if bottomNumber != None:
            if topNumber != None:
                embed = discord.Embed(title="Random number from {} to {}".format(bottomNumber, topNumber), colour=var.embed, description=random.randint(int(bottomNumber), int(topNumber)))
                await ctx.send(embed=embed)
            if topNumber == None:
                embed = discord.Embed(title="Random number from 1 to {}".format(bottomNumber), colour=var.embed, description=random.randint(1, int(bottomNumber)))
                await ctx.send(embed=embed)
        if bottomNumber == None:
            embed = discord.Embed(title="Random number", colour=var.embed, description=f"""
Random number from **1** to **10:** {random.randint(1, 10)}
Random number from **1** to **100:** {random.randint(1, 100)}
Random number from **1** to **1000:** {random.randint(1, 1000)}
Random number from **1** to **1,000,000**: {random.randint(1, 1000000)}""")
            await ctx.send(embed=embed)
    
    @commands.command(name="google", description="[query]|Search google", aliases=["search", "googlesearch", "google-search"])
    async def google(self, ctx, *, query):
        search = await google.search(query, num_results=10)

        embed = discord.Embed(title=f"Results for: {query}", color=var.embed)

        for result in search[:-1]:
            viewURL = ('.'.join(result.url.split('.')[1:]) if 'www.' in result.url else '/'.join(result.url.split('/')[2:]))[0:30] + "..."
            embed.add_field(name=result.title, value=f"[{viewURL}]({result.url}) - {result.description}", inline=False)
        
        await ctx.send(embed=embed)
    
    @commands.command(name="hyperlink", description="[url] [message]|Make a hyperlink")
    async def hyperlink(self, ctx, url, *, message):
        
        if "http" not in url:
            url = "http://" + url + "/"
        try:
            em = discord.Embed(title=message, url=url, colour=var.embed)
            await ctx.send(embed=em)
            await ctx.message.delete()
        except:
            await ctx.send("> Could not find a valid URL.")
    
    @commands.command(name="wikipedia", description="[search]|Search wikipedia for an article")
    async def wikipedia(self, ctx, *, search):
        try:
            summary = wikipedia.summary(search, sentences=5, auto_suggest=False)
        except Exception as e:
            summary = "Could not find article! Did you mean: \n`" + ("`, `".join(str(e).split("\n")[1:20])) + "`"

        embed = discord.Embed(title=f"Here is a wikipedia article for {search}.", description=summary, colour=var.embed)
        await ctx.send(embed=embed)
    
    @commands.command(name="userinfo", description="*[user]|Check info for a user", aliases=['memberinfo'])
    async def userinfo(self, ctx, user: discord.User = None):
        if user == None:
            user = ctx.author
        member = ctx.guild.get_member(user.id)
        embed = discord.Embed(title ="Information For " + str(user), color=var.embed)
        embed.add_field(name="Username", value=user.name)
        embed.add_field(name="User ID", value=user.id)
        embed.add_field(name="User Creation Date", value=user.created_at.strftime("%d %b %Y, %I:%M %p (GMT)"))
        if member != None:
            embed.add_field(name="User Join Date", value=member.joined_at.strftime("%d %b %Y, %I:%M %p (GMT)"))
            embed.add_field(name="Color", value=member.color)
            embed.add_field(name="Users Highest Role", value=member.top_role.mention)
        else:
            embed.set_footer(text="This user is from another server.")
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)
            
    @commands.command(name="serverinfo", description="|Get info on the server", aliases=['guildinfo', 'server-info', 'guild-info'])
    @commands.guild_only()
    async def serverinfo(self, ctx):
        embed = discord.Embed(title="Information For " + ctx.message.guild.name, color=var.embed)
        embed.add_field(name="Server Name", value= ctx.message.guild.name)
        embed.add_field(name="Server ID", value= ctx.message.guild.id)
        embed.add_field(name="Server Creation Date", value= ctx.message.guild.created_at.strftime("%a %d %b %Y at %I:%M %p (GMT)"))
        embed.add_field(name="Server Region", value= ctx.message.guild.region)
        embed.add_field(name="Verification level", value= str(ctx.message.guild.verification_level))
        embed.add_field(name="Owner", value= ctx.message.guild.owner.mention)
        embed.set_thumbnail(url=ctx.message.guild.icon_url)
        embed.set_footer(text=f"See more info with {functions.prefix(ctx.guild)}serverstats")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="serverstatistics", description="|Get stats for the server", aliases=['serverstats', 'srvrstats', 'server-stats', 'server-statistics'])
    @commands.guild_only()
    async def serverstatistics(self, ctx):
        embed = discord.Embed(title="{}'s Server statistics".format(ctx.guild.name), color=var.embed)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Members", value=len(ctx.guild.members))
        embed.add_field(name="Bots", value=str(sum(member.bot for member in ctx.message.guild.members)))
        embed.add_field(name="Administrators", value=str(sum(member.guild_permissions.administrator and not member.bot for member in ctx.message.guild.members)))
        embed.add_field(name="Roles", value=len(ctx.guild.roles))
        embed.add_field(name="Channels", value=len(ctx.guild.channels))
        embed.add_field(name="Age", value=f"{(datetime.now() - ctx.guild.created_at).days} days")
        embed.set_footer(text=f"See more info with {functions.prefix(ctx.guild)}serverinfo")

        await ctx.send(embed=embed)
    
    @commands.command(name="convert", description="[convertType] [convertInput]|Convert from morse or binary to text (and vice versa)", aliases=['convert-from', 'convertfrom', 'converter'])
    async def convert(self, ctx, convertType, *, convertInput):
        if convertType.lower() not in ["morse", "morsecode", "morse-code"] + ["ascii", "binary"]:
            raise customerror.CustomErr(f"Invalid convert type! Please use {functions.prefix(ctx.guild)}convert [ascii/morse] [input to convert]")

        embed = discord.Embed(
            title="Converted successfully!", 
            description=
                "```" + 
                (convert.detect.morsestring(convertType) if convertType.lower() in ["morse", "morsecode", "morse-code"] else convert.detect.asciistring(convertInput, return_type=str) if convertType.lower() in ["ascii", "binary"] else "_ _") + 
                f"```\nConvert it back with `{functions.prefix(ctx.guild)}{convertType} [{convertType}/text]`", 
            color=var.embed
        )
        embed.set_footer(text="Command made with EasyConversion {} | tiny.cc/EasyConversion".format(info.version.current.name))
        try:
            await ctx.send(embed=embed)
        except:
            await ctx.send("> Output too long!")
    
    @commands.command(name="avatar", description="*[member]|Get a user's profile picture", aliases=['pfp', 'logo', 'profilepicture', 'useravatar'])
    async def avatar(self, ctx, user : discord.User = None):
        if user == None:
            user = ctx.message.author
        embed = discord.Embed(title="{}'s avatar".format(user.display_name), color=var.embed)
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)
    
    @commands.command(name="remind", description="[time] [message]|Send a message in a certain amount of time", aliases = ['reminder', 'remindme'])
    async def remind(self, ctx, time = None, *, reminder = None):
        if time == None or reminder == None:
            em = discord.Embed(title="Remind", description='`hb/remind [number (minutes)] [message]`', colour=var.embedFail)
            await ctx.send(embed=em)
        else:
            times = re.sub('[abcdefghijklmnopqrstuvwxyz]', '', time)
            try:
                time = int(times) * 60
            except:
                raise customerror.MildErr("Invalid time! Time must be a number above 1.")
            if time < 1:
                raise customerror.MildErr("Invalid time! Time must be a number above 1.")

            messaged = await ctx.send("> I will send a message in " + str(times) + " minute(s)")

            await asyncio.sleep(5)

            try:
                await messaged.delete()
                await ctx.message.delete()
            except:
              pass

            await asyncio.sleep(int(time - 5))
            await ctx.send(embed=
                discord.Embed(
                    title=f"Reminder from {ctx.message.author}",
                    description=reminder,
                    color=var.embed
                )
            )
    
    @commands.command(name="timer", description="[length (m/s/h)]|Create a timer")
    async def timer(self, ctx, time, time2=None):
        try:
            if time2 == None:
                amount = int(functions.calculateTime(time))
            else:
                if True in [c in str(input) for c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUV1234567890!@#$%^&*()=+;'\[]:"]:
                    amount = int(functions.calculateTime(time)) + int(functions.calculateTime(time2))
        except:
            raise customerror.MildErr("Invalid time! Time must be a number above 1.")
        
        if amount < 1:
            raise customerror.MildErr("Invalid time! Time must be a number above 1.")

        await ctx.send("> Started timer for " + str(amount) + " seconds")
        await asyncio.sleep(amount)
        await ctx.send(f"> Timer for `{str(amount)}` seconds from `{ctx.message.author}` ended.", allowedmentions=discord.AllowedMentions(everyone=False, roles=False))
        
def setup(bot):
    bot.add_cog(Utility1(bot))