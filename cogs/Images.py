from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime, timedelta
import requests, aiohttp, asyncio
from PIL import Image, ImageDraw, ImageFont

from discord.commands import slash_command, Option

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.runtimeDadJoke = {}

    @slash_command(name="minecraft", description="Make a minecraft achievement", aliases=["achievement", "advancement"])
    async def minecraft(self, ctx, text : str):

        img = Image.open("Images/hqdefault.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("Images/Minecraft.ttf", 23)
        draw.text((90, 182), text, (255, 255, 255), font=font)
        img.save('Images/ignoreme' + str(ctx.author.id) + '.png')
        await ctx.respond(file=discord.File('Images/ignoreme' + str(ctx.author.id) + '.png'))
        os.remove('Images/ignoreme' + str(ctx.author.id) + '.png')

    @slash_command(name="whiteboard", description="Write on a whiteboard", aliases=["write"])
    async def whiteboard(self, ctx, text : str):

        img = Image.open("Images/Whiteboard.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("Images/Pretty Girls Script Demo.ttf", 50)
        draw.text((60, 100), text, (0, 0, 0), font=font)
        img.save('Images/ignoreme' + str(ctx.author.id) + '.png')
        await ctx.respond(file=discord.File('Images/ignoreme' + str(ctx.author.id) + '.png'))
        os.remove('Images/ignoreme' + str(ctx.author.id) + '.png')

    @slash_command(name="rip", description="Make a grave for a user", aliases=["grave"])
    async def rip(self, ctx, user : Option(str, description="The user or text to add to a grave") = None):
        randomnumber = str(random.randint(1,10000000000))

        if user == None:
            content = ctx.author.display_name
        else:
            if user.replace("<", "").replace(">", "").replace("@", "").replace("!", "").isdigit():
                for member in ctx.guild.members:
                    if member.id == int(user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")):
                        content = member.display_name
            else:
                content = user

        if len(content) > 24:
            raise customerror.CustomErr("Max characters is 24!")

        if len(content) > 10:
            font = ImageFont.truetype("Images/American Captain.otf", 50)
        if len(content) < 10:
            font = ImageFont.truetype("Images/American Captain.otf", 100)
        
        img = Image.open("Images/rip.png")
        draw = ImageDraw.Draw(img)
        draw.text((131, 399), content, (0, 0, 0), font=font)
        img.save('Images/ignoreme' + str(randomnumber) + '.png')
        await ctx.respond(file=discord.File('Images/ignoreme' + str(randomnumber) + '.png'))
        os.remove('Images/ignoreme' + str(randomnumber) + '.png')

def setup(bot):
    bot.add_cog(Images(bot))