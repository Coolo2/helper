from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror, functions, image
from datetime import datetime, timedelta
import requests, aiohttp, asyncio
import emoji as emojis
import inspect
from discord.ext.commands import MemberConverter
import re
from PIL import Image, ImageEnhance
import io
import threading

from discord import app_commands

guilds = {}

async def mimic_autocomplete(ctx : discord.Interaction, current : str):
    with open("databases/userSettings.json") as f:
        options = json.load(f)
    
    members = [] 
    for member in ctx.guild.members:
        if (
            str(member.id) not in options 
            or "disableMimic" not in options[str(member.id)] 
            or str(ctx.guild.id) not in options[str(member.id)]["disableMimic"]
            or not options[str(member.id)]["disableMimic"][str(ctx.guild.id)]
        ):

            if not current or current.lower() in member.name.lower() or current.lower() in str(member.nick).lower():
                
                if member.nick:
                    members.append(app_commands.Choice(name=f"{member.nick} ({member})", value=f"{member.nick} ({member})"))
                else:
                    members.append(app_commands.Choice(name=str(member), value=str(member)))
    
    if current in "disable enable":
        members.append(app_commands.Choice(name="Disable", value="disable"))
        members.append(app_commands.Choice(name="Enable", value="enable"))

    return members[:25]

class Fun1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.runtimeDadJoke = {}

    @app_commands.command(name="deepfry", description="Deepfry an image")
    @app_commands.describe(user_url="A user or URL to deepfry the image of", attachment="An optional attachment to deepfry")
    async def deepfry(
        self, 
        ctx : discord.Interaction, 
        user_url : str = None,
        attachment : discord.Attachment = None
    ):  
        args = user_url
        if attachment:
            args = attachment.url
        
        await ctx.response.defer()
        
        imgURL = await functions.imageFromArg(ctx, args, ("image/png", "image/jpeg", "image/jpg"), ["png", "jpg", "jpeg"])
        if imgURL == False:
            raise customerror.MildErr("Could not find image! This command support png and jpeg images only.")
        try:

            async with aiohttp.ClientSession() as session:
                async with session.get(imgURL) as r:

                    img = Image.open(io.BytesIO(await r.read()))

                    img = await image.deepfry(img)

                    with io.BytesIO() as image_binary:
                        img.save(image_binary, 'PNG')
                        image_binary.seek(0)

                        await ctx.followup.send(file=discord.File(fp=image_binary, filename='image.png'))

        except Exception as e:
            raise customerror.CustomErr("Unknown image error occurred. Maybe try another image? " + str(e))
    
    @app_commands.command(name="blurpify", description="Blurpify an image")
    @app_commands.describe(user_url="A user or URL to deepfry the profile picture of", attachment="An optional attachment to replace the user avatar")
    async def blurpify(
        self, 
        ctx : discord.Interaction, 
        user_url : str = None,
        attachment : discord.Attachment = None
    ):  
        args = user_url
        if attachment:
            args = attachment.url
        
        await ctx.response.defer()

        imgURL = await functions.imageFromArg(ctx, args, ("image/png", "image/jpeg", "image/jpg", "image/gif"), ["png", "jpg", "jpeg", "gif"])
        if imgURL == False:
            raise customerror.MildErr("Could not find image! This command support png, jpeg and gif images only.")

        try:

            async with aiohttp.ClientSession() as session:
                async with session.get(imgURL) as r:

                    img = Image.open(io.BytesIO(await r.read()))

                    img = await image.blurpify(img)

                    with io.BytesIO() as image_binary:
                        img.save(image_binary, 'PNG')
                        image_binary.seek(0)

                        await ctx.followup.send(file=discord.File(fp=image_binary, filename='image.png'))
        except Exception as e:
            raise customerror.CustomErr("Unknown image error occurred. Maybe try another image? " + str(e))
    
    @app_commands.command(name="randomword", description="Get random words in the English language")
    async def randomword(self, ctx : discord.Interaction):
        with open("resources/allWords.json") as f:
            words = json.load(f)
        amount = random.randint(15, 30)
        return await ctx.response.send_message(
            embed=discord.Embed(
                title=random.choice(["Random words", f"{amount} random words", f"Found {amount} random words!", f"Here's the {amount} random words!"]), 
                description=", ".join([random.choice(words) for i in range(1, amount)]).capitalize() + f" and {random.choice(words)}.", 
                colour=var.embed
            )
        )
    
    @app_commands.command(name="dadjoke", description="Get a random dad joke")
    async def dadjoke(self, ctx : discord.Interaction):
        await ctx.response.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com/", headers={"Accept":"application/json"}) as r:
                json = await r.json()
                e = discord.Embed(
                    title=random.choice(["Here's a dad joke for you!", "Random dad joke!", "Here's a dad joke!"]), 
                    description=json["joke"], 
                    colour=var.embed
                )
                self.runtimeDadJoke[str(ctx.channel.id)] = True
                await ctx.followup.send(embed=e)
    
    @app_commands.command(name="fact", description='Get a random fact')
    async def fact(self, ctx : discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as r:
                json = await r.json()
                e = discord.Embed(title=random.choice(["Did you know that...", "Random fact"]), description=json['text'].replace("`", "'"), colour=var.embed)
                await ctx.response.send_message(embed=e)
    
    @app_commands.command(name="clap", description="Add clap emojis between the message")
    @app_commands.describe(message="The message to clap")
    async def clap(self, ctx : discord.Interaction, message : str):
        emoji = ":clap:"
        
        return await ctx.response.send_message(emoji + " " + message.replace(" ", f" {emoji} ") + " " + emoji, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
    
    @app_commands.command(name="meme", description="Get a random reddit post")
    @app_commands.describe(subreddit="The subreddit to get a random post from")
    async def meme(self, ctx : discord.Interaction, subreddit : str = None):
        await ctx.response.defer()

        defaultSubreddit = random.choice(["memes", "meme", "cleanmeme", "dankmeme"])

        if subreddit == None:
            subreddit = defaultSubreddit
        
        subreddit = subreddit.replace("r/", "")

        async with aiohttp.ClientSession() as session:

            foundImage = False 
            counter = 0

            while not foundImage:
                counter += 1
                if counter >= 10:
                    raise customerror.MildErr("Couldn't find an image, please try again.")
                    
                    
                async with session.get("https://api.reddit.com/r/{}/random?obey_over18=true".format(subreddit)) as r:
                    try:
                        
                        data = await r.json()

                        url = data[0]["data"]["children"][0]["data"]["url"]
                        willit = functions.uri_validator(url)

                        if willit == True and True in [fileType in url for fileType in [".jpeg", ".png", ".gif", ".jpg", ".webp"]]:
                            
                            user = data[0]["data"]["children"][0]["data"]["author"]
                            upvotes = data[0]["data"]["children"][0]["data"]["ups"]
                            link = data[0]["data"]["children"][0]["data"]["permalink"]

                            e = discord.Embed(title="Post from r/{}".format(subreddit), description=f"<:upvote:855721570483175424> {upvotes:,d}\n[Visit](https://reddit.com{link})", colour=var.embed)
                            e.set_image(url=url)
                            e.set_footer(text=f"u/{user}")

                            await ctx.followup.send(embed=e)
                            foundImage = True
                        
                    except Exception as e:
                        print(e)
                        if str(e) == "Couldn't find an image, please try again.":
                            raise e
                        raise customerror.MildErr("Invalid Subreddit or marked NSFW")
    
    @app_commands.command(name="cat", description="Get a random cat image")
    async def cat(self, ctx : discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://cataas.com/cat?json=true') as r:
                data = await r.json()

                if r.status == 200:
                    e = discord.Embed(title=random.choice(["Meow!", "Random cat!"]), colour=var.embed)
                    e.set_image(url="https://cataas.com" + data["url"])
                    await ctx.response.send_message(embed=e)
                else:
                    raise customerror.CustomErr("Could not access API. Try again?")

    @app_commands.command(name="dog", description="Get a random dog image")
    async def dog(self, ctx : discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://random.dog/woof.json') as r:
                data = await r.json()

                if r.status == 200:
                    e = discord.Embed(title=random.choice(["Woof!", "Random dog!"]), colour=var.embed)
                    e.set_image(url=data["url"])
                    await ctx.response.send_message(embed=e)
                else:
                    raise customerror.CustomErr("Could not access API. Try again?")
    
    @app_commands.command(name="spoiler", description="Make a message into a special spoiler")
    @app_commands.describe(message="The message to spoil")
    async def spoiler(self, ctx : discord.Interaction, message : str):
        final = "```"
        for character in message:
            if character == " ":
                character = "_ _"
            final = final + "||" + character + "||"
        final = final + "```"
        try:
            await ctx.response.send_message(final, ephemeral=True)
        except Exception as e:
            raise customerror.MildErr("Final response too long!")
    
    @app_commands.command(name="emoji", description="Emojify a message")
    @app_commands.describe(message="The message to emojify")
    async def emojify(self, ctx : discord.Interaction, message : str):
        finalstring = ""
        for character in message:
            if character.lower() in "abcdefghijklmnopqrstuvwxyz":
                finalstring = finalstring + ":regional_indicator_{}: ".format(character.lower())
            else:
                finalstring = finalstring + " {} ".format(character)
        try:
            await ctx.response.send_message(finalstring, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        except Exception as e:
            raise customerror.MildErr("Final response too long!")
    
    class MemberConverterClass():
        def __init__(self, interaction : discord.Interaction, bot : commands.Bot):
            self.bot = bot 

            self.author = interaction.user 
            self.guild = interaction.guild
            self.user = interaction.user
            self.channel = interaction.channel
            self.response = interaction.response

    @app_commands.command(name="mimic", description="Mimic another user!")
    @app_commands.describe(member="The member to mimic (Can be enable/disable to toggle mimicking for yourself)", message="The message to send as the member")
    @app_commands.autocomplete(member=mimic_autocomplete)
    async def mimic(
            self, 
            ctx : discord.Interaction, 
            member : str, 
            message : str
    ):
        ctx = self.MemberConverterClass(ctx, self.bot)

        start_time = datetime.now()

        converter = MemberConverter()
        data = await functions.read_data("databases/userSettings.json")

        if member.lower() not in ["disable", "enable"]:
            if "(" in member.lower():
                brackets = re.findall('\(.*?\)', member)
                member = await converter.convert(ctx, brackets[-1][1:][:-1])
            else:
                member = await converter.convert(ctx, member)
        else:
            if str(ctx.user.id) not in data:
                data[str(ctx.user.id)] = {}
            
            if "disableMimic" not in data[str(ctx.user.id)]:
                data[str(ctx.user.id)]["disableMimic"] = {}

            data[str(ctx.user.id)]["disableMimic"][str(ctx.guild.id)] = True if member.lower() == "disable" else False

            await functions.save_data("databases/userSettings.json", data)
            await functions.read_load("databases/userSettings.json", data)

            return await ctx.response.send_message(embed=
                discord.Embed(
                    title="Successfully " + ("enabled" if member.lower() == "enable" else "disabled") + "!",
                    description="Successfully **" + ("enabled" if member.lower() == "enable" else "disabled") + "** other members mimicking you **in this server**!",
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
        
        if str(ctx.user.id) not in data:
            data[str(ctx.user.id)] = {}
        if "data" not in data[str(ctx.user.id)]:
            data[str(ctx.user.id)]["data"] = {}
        if "mimicPrompt" not in data[str(ctx.user.id)]["data"]:
            data[str(ctx.user.id)]["data"]["mimicPrompt"] = True

            await ctx.response.send_message(f"Top tip! You can use `{functions.prefix(ctx.guild)}mimic [enable/disable]` to disable/enable someone mimicking you on this server!", ephemeral=True)
        
        try:
            webhooks = await ctx.channel.webhooks()

            if len(webhooks) == 0:
                webhook = await ctx.channel.create_webhook(name="Helper Webhook")
            else:
                webhook = webhooks[0]
        except Exception as e:
            print(e)
            raise commands.BotMissingPermissions(["manage_webhooks"])

        if not ctx.user.guild_permissions.mention_everyone:
            allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
        else:
            allowed_mentions = discord.AllowedMentions(everyone=True, roles=True, users=True)

        await webhook.send(
            content=message,
            avatar_url=str(member.avatar.url) if member.avatar else None,
            username=member.display_name,
            allowed_mentions=allowed_mentions,
            wait=False
        )

        timeElapsed = round((datetime.now() - start_time).total_seconds(), 3)

        await ctx.response.send_message(f"Complete `{timeElapsed}s`", ephemeral=True)

        await functions.save_data("databases/userSettings.json", data)
        await functions.read_load("databases/userSettings.json", data)
        

async def setup(bot):
    await bot.add_cog(Fun1(bot), guilds=var.guilds)