from discord.ext import commands 
import discord

import random, json
from setup import var
from functions import functions, image
from datetime import datetime
import aiohttp
import inspect
from PIL import Image
import io

import helper

from discord import app_commands

guilds = {}

class Fun1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.runtimeDadJoke = {}

    @app_commands.command(name="deepfry", description="Deepfry an image")
    @app_commands.describe(user="A user to deepfry the image of", url="A url-image to deepfry", attachment="An optional attachment to deepfry")
    async def deepfry(
        self, 
        ctx : discord.Interaction, 
        user : discord.User = None,
        url : str = None,
        attachment : discord.Attachment = None
    ):  
        ourl = url
        if not url:
            url = ctx.user.display_avatar.url if ctx.user.display_avatar else None
        if attachment:
            url = attachment.url
        if user and user.display_avatar:
            url = user.display_avatar.url
        
        await ctx.response.defer()
        
        imgValidation = await functions.is_url_image(url, ("image/png", "image/jpeg", "image/jpg", "image/gif"))
        if imgValidation == False:
            raise helper.errors.MildErr("Could not find image! This command support png, jpeg and gif images only.")
        
        try:

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:

                    img = Image.open(io.BytesIO(await r.read()))

                    img = await image.deepfry(img)

                    with io.BytesIO() as image_binary:
                        img.save(image_binary, 'PNG')
                        image_binary.seek(0)

                        embed = discord.Embed(title="Deepfried!", color=var.embed)
                        embed.set_image(url="attachment://image.png")
                        if user == None and ourl == None and attachment == None:
                            embed.set_footer(text="Tip! You can attach a user ping, image file or url if you add arguments to the command!")

                        await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename='image.png'))

        except Exception as e:
            raise helper.errors.CustomErr("Unknown image error occurred. Maybe try another image? " + str(e))
    
    @app_commands.command(name="blurpify", description="Blurpify an image")
    @app_commands.describe(user="A user or URL to deepfry the profile picture of", url="A url-image to deepfry", attachment="An optional attachment to replace the user avatar")
    async def blurpify(
        self, 
        ctx : discord.Interaction, 
        user : discord.User = None,
        url : str = None,
        attachment : discord.Attachment = None
    ):  
        ourl = url
        if not url:
            url = ctx.user.display_avatar.url if ctx.user.display_avatar else None
        if attachment:
            url = attachment.url
        if user and user.display_avatar:
            url = user.display_avatar.url

        imgValidation = await functions.is_url_image(url, ("image/png", "image/jpeg", "image/jpg", "image/gif"))
        if imgValidation == False:
            raise helper.errors.MildErr("Could not find image! This command support png, jpeg and gif images only.")
        
        await ctx.response.defer()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:

                    img = Image.open(io.BytesIO(await r.read()))

                    img = await image.blurpify(img)

                    with io.BytesIO() as image_binary:
                        img.save(image_binary, 'PNG')
                        image_binary.seek(0)

                        embed = discord.Embed(title=random.choice(["Blurp!", "Blurpified!"]), color=var.embed)
                        embed.set_image(url="attachment://image.png")
                        if user == None and ourl == None and attachment == None:
                            embed.set_footer(text="Tip! You can attach a user ping, image file or url if you add arguments to the command!")

                        await ctx.followup.send(embed=embed, file=discord.File(fp=image_binary, filename='image.png'))
        except Exception as e:
            raise helper.errors.CustomErr("Unknown image error occurred. Maybe try another image? " + str(e))
    
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
                    raise helper.errors.MildErr("Couldn't find an image, please try again.")
                    
                    
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
                        raise helper.errors.MildErr("Invalid Subreddit or marked NSFW")
    
    @app_commands.command(name="cat", description="Get a random cat image")
    async def cat(self, ctx : discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.thecatapi.com/v1/images/search?format=json') as r:
                data = await r.json()

                if r.status == 200:
                    e = discord.Embed(title=random.choice(["Meow!", "Random cat!"]), colour=var.embed)
                    e.set_image(url=data[0]["url"])
                    await ctx.response.send_message(embed=e)
                else:
                    raise helper.errors.CustomErr("Could not access API. Try again?")

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
                    raise helper.errors.CustomErr("Could not access API. Try again?")
    
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
            raise helper.errors.MildErr("Final response too long!")
    
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
            raise helper.errors.MildErr("Final response too long!")
    

    
    mimic = app_commands.Group(name="mimic", description="Mimic another user!", guild_only=True)

    @mimic.command(name="toggle", description="Toggle (enable/disable) mimicking for yourself")
    async def _mimic_toggle(self, interaction : discord.Interaction):
        data = await functions.read_data("databases/userSettings.json")

        if str(interaction.user.id) not in data:
            data[str(interaction.user.id)] = {}
        
        if "disableMimic" not in data[str(interaction.user.id)]:
            data[str(interaction.user.id)]["disableMimic"] = {}

        data[str(interaction.user.id)]["disableMimic"][str(interaction.guild.id)] = True if not data[str(interaction.user.id)]["disableMimic"].get(str(interaction.guild.id)) else False

        s = "enabled" if data[str(interaction.user.id)]["disableMimic"][str(interaction.guild.id)] == False else "disabled"

        await interaction.response.send_message(embed=
            discord.Embed(
                title=f"Successfully {s}!",
                description=f"Successfully **{s}** other members mimicking you **in this server**!",
                color=var.embed
            )
        )

        await functions.save_data("databases/userSettings.json", data)

    @mimic.command(name="mimic", description="Mimic another user!")
    @app_commands.describe(user="The member to mimic (Can be enable/disable to toggle mimicking for yourself)", message="The message to send as the member")
    async def _mimic(
            self, 
            ctx : discord.Interaction, 
            user : discord.User, 
            message : str
    ):

        start_time = datetime.now()

        data = await functions.read_data("databases/userSettings.json")

        if message == None:
            raise commands.MissingRequiredArgument(inspect.Parameter("message", kind=inspect.Parameter.POSITIONAL_ONLY))
        
        if str(user.id) in data:
            if "disableMimic" in data[str(user.id)]:
                if str(ctx.guild.id) in data[str(user.id)]["disableMimic"]:
                    if data[str(user.id)]["disableMimic"][str(ctx.guild.id)] == True:
                        raise helper.errors.MildErr(user.mention + " has disabled mimicking for this server!")
        
        if str(ctx.user.id) not in data:
            data[str(ctx.user.id)] = {}
        if "data" not in data[str(ctx.user.id)]:
            data[str(ctx.user.id)]["data"] = {}
        if "mimicPrompt" not in data[str(ctx.user.id)]["data"]:
            data[str(ctx.user.id)]["data"]["mimicPrompt"] = True

            await ctx.response.send_message(f"Top tip! You can use `/mimic [enable/disable]` to disable/enable someone mimicking you on this server!", ephemeral=True)
        
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
            avatar_url=str(user.display_avatar.url) if user.display_avatar else None,
            username=user.display_name,
            allowed_mentions=allowed_mentions,
            wait=False
        )

        timeElapsed = round((datetime.now() - start_time).total_seconds(), 3)

        await ctx.response.send_message(f"Complete `{timeElapsed}s`", ephemeral=True)
        

async def setup(bot):
    await bot.add_cog(Fun1(bot))