from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

from discord import app_commands

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.runtimeDadJoke = {}

    @app_commands.command(name="minecraft", description="Make a minecraft achievement")
    async def minecraft(self, ctx : discord.Interaction, text : str):

        img = Image.open("Images/hqdefault.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("Images/Minecraft.ttf", 23)
        draw.text((90, 182), text, (255, 255, 255), font=font)
        img.save('Images/ignoreme' + str(ctx.user.id) + '.png')
        await ctx.response.send_message(file=discord.File('Images/ignoreme' + str(ctx.user.id) + '.png'))
        os.remove('Images/ignoreme' + str(ctx.user.id) + '.png')

    @app_commands.command(name="whiteboard", description="Write on a whiteboard")
    async def whiteboard(self, ctx : discord.Interaction, text : str):

        img = Image.open("Images/Whiteboard.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("Images/Pretty Girls Script Demo.ttf", 50)
        draw.text((60, 100), text, (0, 0, 0), font=font)
        img.save('Images/ignoreme' + str(ctx.user.id) + '.png')
        await ctx.response.send_message(file=discord.File('Images/ignoreme' + str(ctx.user.id) + '.png'))
        os.remove('Images/ignoreme' + str(ctx.user.id) + '.png')

    @app_commands.command(name="rip", description="Make a grave for a user")
    @app_commands.describe(user="A mention or text to make a grave for")
    async def rip(self, ctx : discord.Interaction, user : str = None):
        randomnumber = str(random.randint(1,10000000000))

        if user == None:
            content = ctx.user.display_name
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
        await ctx.response.send_message(file=discord.File('Images/ignoreme' + str(randomnumber) + '.png'))
        os.remove('Images/ignoreme' + str(randomnumber) + '.png')

async def setup(bot):
    await bot.add_cog(Images(bot), guilds=var.guilds)