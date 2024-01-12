from discord.ext import commands 
import discord

import random, os
from PIL import Image, ImageDraw, ImageFont
import helper
import io
import textwrap

from discord import app_commands

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.font_pretty_girls_script = ImageFont.truetype("images/Pretty Girls Script Demo.ttf", 50)
        self.font_minecraft = ImageFont.truetype("images/Minecraft.ttf", 23)
        self.font_american_captain = ImageFont.truetype("images/American Captain.otf", 50)

    @app_commands.command(name="minecraft_achievement", description="Make a minecraft achievement")
    async def minecraft_achievement(self, ctx : discord.Interaction, text : str):

        buf = io.BytesIO()

        img = Image.open("images/hqdefault.png")
        draw = ImageDraw.Draw(img)
        

        draw.text((90, 55), text, (255, 255, 255), font=self.font_minecraft)

        img.save(buf, format="PNG")
        buf.seek(0)

        await ctx.response.send_message(file=discord.File(buf, "image.png"))

    @app_commands.command(name="whiteboard", description="Write on a whiteboard")
    async def whiteboard(self, ctx : discord.Interaction, text : str):
        
        buf = io.BytesIO()

        img = Image.open("images/Whiteboard.png")
        draw = ImageDraw.Draw(img)
        

        draw.multiline_text((60, 50), "\n".join(textwrap.wrap(text, width=24)), (0, 0, 0), font=self.font_pretty_girls_script, spacing=20)

        img.save(buf, format="PNG")
        buf.seek(0)

        await ctx.response.send_message(file=discord.File(buf, "image.png"))

    @app_commands.command(name="rip", description="Make a grave for a user")
    @app_commands.describe(user="A mention or text to make a grave for")
    async def rip(self, ctx : discord.Interaction, user : str = None):

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
            raise helper.errors.CustomErr("Max characters is 24!")
        
        
        
        buf = io.BytesIO()
        
        img = Image.open("images/rip.png")
        draw = ImageDraw.Draw(img)
        draw.text((img.width//2, 399), content, (0, 0, 0), font=self.font_american_captain, anchor="mm")

        img.save(buf, format="PNG")
        buf.seek(0)

        await ctx.response.send_message(file=discord.File(buf, "image.png"))

async def setup(bot):
    await bot.add_cog(Images(bot))