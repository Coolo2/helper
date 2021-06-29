import discord, random, os, json
from discord.ext import commands
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime, timedelta
import requests, aiohttp, asyncio
from PIL import Image, ImageDraw, ImageFont

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.runtimeDadJoke = {}

    @commands.command(name="minecraft", description="[text]|Make a minecraft achievement", aliases=["achievement", "advancement"])
    async def minecraft(self, ctx, *, text):

        img = Image.open("Images/hqdefault.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("Images/Minecraft.ttf", 23)
        draw.text((90, 182), text, (255, 255, 255), font=font)
        img.save('Images/ignoreme' + str(ctx.message.author.id) + '.png')
        await ctx.send(file=discord.File('Images/ignoreme' + str(ctx.message.author.id) + '.png'))
        os.remove('Images/ignoreme' + str(ctx.message.author.id) + '.png')

    @commands.command(name="whiteboard", description="[text]|Write on a whiteboard", aliases=["write"])
    async def whiteboard(self, ctx, *, text):
        area = ctx.message.channel

        img = Image.open("Images/Whiteboard.png")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("Images/Pretty Girls Script Demo.ttf", 50)
        draw.text((60, 100), text, (0, 0, 0), font=font)
        img.save('Images/ignoreme' + str(ctx.message.author.id) + '.png')
        await ctx.send(file=discord.File('Images/ignoreme' + str(ctx.message.author.id) + '.png'))
        os.remove('Images/ignoreme' + str(ctx.message.author.id) + '.png')

    @commands.command(name="rip", description="*[@user/text]|Make a grave for a user", aliases=["grave"])
    async def rip(self, ctx, *, user = None):
        randomnumber = str(random.randint(1,10000000000))

        if user == None:
            content = ctx.message.author.display_name
        else:
            if "<@" in user:
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
        await ctx.send(file=discord.File('Images/ignoreme' + str(randomnumber) + '.png'))
        os.remove('Images/ignoreme' + str(randomnumber) + '.png')

def setup(bot):
    bot.add_cog(Images(bot))