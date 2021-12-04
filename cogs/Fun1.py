from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime, timedelta
import requests, aiohttp, asyncio
import emoji as emojis
from discordwebhook import asyncCreate
import inspect
from discord.ext.commands import MemberConverter

from discord.commands import slash_command, Option

class Fun1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.runtimeDadJoke = {}

    @slash_command(name="deepfry", description="Deepfry an image", aliases=["fry", "deep-fry"])
    async def deepfry(self, ctx, args : Option(str, name="user-url", description="A user or URL to deepfry the image of", required=False) = None):
        imgURL = await functions.imageFromArg(ctx, args, ("image/png", "image/jpeg", "image/jpg"), ["png", "jpg", "jpeg"])
        if imgURL == False:
            raise customerror.MildErr("Could not find image! This command support png and jpeg images only.")
        try:
            loadingMsg = await ctx.respond("> Deepfrying image...")
            loadingMsg = await loadingMsg.original_message()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://nekobot.xyz/api/imagegen?type=deepfry&image={imgURL}") as r:
                    json = await r.json()
                    e = discord.Embed(title="Deep fried image!", colour=var.embed)
                    e.set_image(url=json['message'])
                    await loadingMsg.edit(content=None, embed=e)
        except Exception as e:
            raise customerror.CustomErr("Unknown image error occurred. Maybe try another image? " + str(e))
    
    @slash_command(name="blurpify", description="Blurpify an image", aliases=["blurp", "blurple"])
    async def blurpify(self, ctx, args : Option(str, name="user-url", description="A user or URL to deepfry the image of", required=False) = None):
        imgURL = await functions.imageFromArg(ctx, args, ("image/png", "image/jpeg", "image/jpg", "image/gif"), ["png", "jpg", "jpeg", "gif"])
        if imgURL == False:
            raise customerror.MildErr("Could not find image! This command support png, jpeg and gif images only.")
        try:
            loadingMsg = await ctx.respond("> Blurpifying image... This can take a while so please wait...")
            loadingMsg = await loadingMsg.original_message()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://nekobot.xyz/api/imagegen?type=blurpify&image={imgURL}") as r:
                    json = await r.json()
                    e = discord.Embed(title="Blurpified image!", colour=var.embed)
                    e.set_image(url=json['message'])
                    await loadingMsg.edit(content=None, embed=e)
        except Exception as e:
            raise customerror.CustomErr("Unknown image error occurred. Maybe try another image? " + str(e))
    
    @slash_command(name="randomword", description="Get random words in the English language", aliases=["randomwords", "random-word", "random-words"])
    async def randomword(self, ctx):
        with open("resources/allWords.json") as f:
            words = json.load(f)
        amount = random.randint(15, 30)
        return await ctx.respond(
            embed=discord.Embed(
                title=random.choice(["Random words", f"{amount} random words", f"Found {amount} random words!", f"Here's the {amount} random words!"]), 
                description=", ".join([random.choice(words) for i in range(1, amount)]).capitalize() + f" and {random.choice(words)}.", 
                colour=var.embed
            )
        )
    
    @slash_command(name="dadjoke", description="Get a random dad joke", aliases=["dad-joke", "dadjokes", "dad-jokes"])
    async def dadjoke(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://us-central1-dadsofunny.cloudfunctions.net/DadJokes/random/jokes") as r:
                json = await r.json()
                e = discord.Embed(
                    title=random.choice(["Here's a dad joke for you!", "Random dad joke!", "Here's a dad joke!"]), 
                    description=json['setup']+ "\n||" + json['punchline'] + "||" + (" <- Click here to see the punchline" if str(ctx.channel.id) not in self.runtimeDadJoke else ""), 
                    colour=var.embed
                )
                self.runtimeDadJoke[str(ctx.channel.id)] = True
                await ctx.respond(embed=e)
    
    @slash_command(name="fact", description='Get a random fact', aliases=['randomfact', 'uselessfact'])
    async def fact(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as r:
                json = await r.json()
                e = discord.Embed(title=random.choice(["Did you know that...", "Random fact"]), description=json['text'].replace("`", "'"), colour=var.embed)
                await ctx.respond(embed=e)
    
    @slash_command(name="clap", description="*[emoji] [message]")
    async def clap(self, ctx, message : Option(str, description="The message to clap")):
        emoji = ":clap:"
        
        return await ctx.respond(emoji + " " + message.replace(" ", f" {emoji} ") + " " + emoji, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
    
    @slash_command(name="colorfilter", description="Blurpify an image", aliases=["colourfilter", "color-filter", "colour-filter"])
    async def colorfilter(self, ctx, color : Option(str, description="The colour to filter"), args : Option(str, name="url_user", description="The URL or user to use the image of", required=False) = None):
        with open("resources/colors.json") as f:
            colors = json.load(f)
        colorHex = ""
        color = color.replace("#", "")
        for colour in colors:
            if colour[1].lower() == color.lower() or colour[0].lower() == color.lower():
                colorHex = colour[0]
        if colorHex == "":
            if len(color) == 6 and False not in [c in "ABCDEF0123456789" for c in color.upper()]:
                colorHex = color 
            else:
                raise customerror.MildErr(f"Invalid color! Make sure it is valid hex (eg: `#FF0000`) or is a valid color name.")
        imgURL = await functions.imageFromArg(ctx, args, ("image/png", "image/jpeg", "image/jpg"), ["png", "jpg", "jpeg"])
        if imgURL == False:
            raise customerror.MildErr("Could not find image! This command support png and jpeg images only.")
        try:
            e = discord.Embed(title="Filted the colors!", colour=var.embed)
            e.set_image(url=f"https://api.no-api-key.com/api/v2/customify?image={str(imgURL).replace('.webp', '').split('?')[0]}&color={colorHex}")
            await ctx.respond(embed=e)
        except Exception as e:
            raise customerror.CustomErr("Unknown image error occurred. Maybe try another image? " + str(e))
    
    @slash_command(name="meme", description="Get a random reddit post", aliases=['randomreddit', 'reddit', 'subreddit', 'redditpost'])
    async def meme(self, ctx, subreddit : Option(str, description="subreddit to find an image from") = None):

        defaultSubreddit = random.choice(["memes", "meme", "cleanmeme", "dankmeme"])

        if subreddit == None:
            subreddit = defaultSubreddit
        
        subreddit = subreddit.replace("r/", "")

        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.reddit.com/r/{}/random?obey_over18=true".format(subreddit)) as r:
                try:
                    data = await r.json()
                    url = data[0]["data"]["children"][0]["data"]["url"]
                    willit = functions.uri_validator(url)

                    if willit == True and True in [fileType in url for fileType in [".jpeg", ".png", ".gif", ".jpeg", ".webp"]]:
                        
                        author = data[0]["data"]["children"][0]["data"]["author"]
                        upvotes = data[0]["data"]["children"][0]["data"]["ups"]

                        e = discord.Embed(title="Post from r/{}".format(subreddit), description=f"u/{author} | <:upvote:855721570483175424> {upvotes}", colour=var.embed)
                        e.set_image(url=url)

                        await ctx.respond(embed=e)
                    else:
                        raise customerror.MildErr("Couldn't find an image, please try again.")
                except Exception as e:
                    if str(e) == "Couldn't find an image, please try again.":
                        raise e
                    raise customerror.MildErr("Invalid Subreddit or marked NSFW")
    
    @slash_command(name="cat", description="Get a random cat image", aliases = ['randomcat'])
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search?format=json') as r:
                data = await r.json()

                if r.status == 200:
                    e = discord.Embed(title=random.choice(["Meow!", "Random cat!"]), colour=var.embed)
                    e.set_image(url=data[0]['url'])
                    await ctx.respond(embed=e)
                else:
                    raise customerror.CustomErr("Could not access API. Try again?")

    @slash_command(name="dog", description="Get a random dog image", aliases = ['randomdog'])
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://random.dog/woof.json') as r:
                data = await r.json()

                if r.status == 200:
                    e = discord.Embed(title=random.choice(["Woof!", "Random dog!"]), colour=var.embed)
                    e.set_image(url=data["url"])
                    await ctx.respond(embed=e)
                else:
                    raise customerror.CustomErr("Could not access API. Try again?")
    
    @slash_command(name="spoiler", description="|Make a message into a special spoiler")
    async def spoiler(self, ctx, message : Option(str, description="The message to spoiler-split")):
        final = "```"
        for character in message:
            if character == " ":
                character = "_ _"
            final = final + "||" + character + "||"
        final = final + "```"
        try:
            await ctx.respond(final, ephemeral=True)
        except:
            raise customerror.MildErr("Final response too long!")
    
    @slash_command(name="emoji", description="Emojify a message", aliases=["emojify"])
    async def emojify(self, ctx, message : Option(str, description="The message to turn into emojis")):
        finalstring = ""
        for character in message:
            if character.lower() in "abcdefghijklmnopqrstuvwxyz":
                finalstring = finalstring + ":regional_indicator_{}: ".format(character.lower())
            else:
                finalstring = finalstring + " {} ".format(character)
        try:
            await ctx.respond(finalstring, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        except:
            raise customerror.MildErr("Final response too long!")
    
    @slash_command(name="mimic", description="Mimic another user!")
    async def mimic(self, ctx, member : Option(discord.Member, description="The member to mimic"), message : Option(str, description="The message to send as the mimic")):
        converter = MemberConverter()
        data = await functions.read_data("databases/userSettings.json")

        if member.lower() not in ["on", "off"]:
            member = await converter.convert(ctx, member)
        else:
            if str(ctx.author.id) not in data:
                data[str(ctx.author.id)] = {}
            
            if "disableMimic" not in data[str(ctx.author.id)]:
                data[str(ctx.author.id)]["disableMimic"] = {}

            data[str(ctx.author.id)]["disableMimic"][str(ctx.guild.id)] = True if member.lower() == "off" else False

            await functions.save_data("databases/userSettings.json", data)
            await functions.read_load("databases/userSettings.json", data)

            return await ctx.respond(embed=
                discord.Embed(
                    title="Successfully " + ("enabled" if member.lower() == "on" else "disabled") + "!",
                    description="Successfully **" + ("enabled" if member.lower() == "on" else "disabled") + "** other members mimicking you **in this server**!",
                    color=var.embed
                )
            )

        if message == None:
            raise commands.MissingRequiredArgument(inspect.Parameter("message", kind=inspect.Parameter.POSITIONAL_ONLY))
        
        if str(member.id) in data:
            if "disableMimic" in data[str(member.id)]:
                if str(ctx.guild.id) in data[str(member.id)]["disableMimic"]:
                    if data[str(member.id)]["disableMimic"][str(ctx.guild.id)] == True:
                        raise customerror.MildErr(member.name + " has disabled mimicking for this server!")
        
        if str(ctx.author.id) not in data:
            data[str(ctx.author.id)] = {}
        if "data" not in data[str(ctx.author.id)]:
            data[str(ctx.author.id)]["data"] = {}
        if "mimicPrompt" not in data[str(ctx.author.id)]["data"]:
            data[str(ctx.author.id)]["data"]["mimicPrompt"] = True

            await ctx.respond(f"Top tip! You can use `{functions.prefix(ctx.guild)}mimic [on/off]` to disable/enable someone mimicking you on this server!")
        
        try:
            webhooks = await ctx.channel.webhooks()

            if len(webhooks) == 0:
                finalwebhook = await ctx.channel.create_webhook(name="Helper Webhook")
            else:
                finalwebhook = webhooks[0]
        except:
            raise commands.BotMissingPermissions(["manage_webhooks"])
        
        main = asyncCreate.Webhook(finalwebhook.url)
        main.avatar.url(str(member.avatar.url))
        main.author(member.display_name)
        main.message(message)
        if not ctx.author.guild_permissions.mention_everyone:
            main.allowed_mentions(everyone=False, roles=False)
        await main.send()

        await functions.save_data("databases/userSettings.json", data)
        await functions.read_load("databases/userSettings.json", data)
        

def setup(bot):
    bot.add_cog(Fun1(bot))