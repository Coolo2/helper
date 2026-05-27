from discord.ext import commands 
import discord

import random, os
from PIL import Image, ImageDraw, ImageFont
import helper
import io
import textwrap
from pathlib import Path

from discord import app_commands

class Images(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.assets_dir = Path(__file__).resolve().parent.parent / "Images"

        self.font_pretty_girls_script = self._load_font("Pretty Girls Script Demo.ttf", 50)
        self.font_minecraft = self._load_font("Minecraft.ttf", 23)
        self.font_american_captain = self._load_font("American Captain.otf", 50)

    def _asset_path(self, filename: str) -> Path:
        return self.assets_dir / filename

    def _load_font(self, filename: str, size: int):
        try:
            return ImageFont.truetype(str(self._asset_path(filename)), size)
        except OSError:
            return ImageFont.load_default()

    @app_commands.command(name="minecraft_achievement", description="Make a minecraft achievement")
    async def minecraft_achievement(self, ctx : discord.Interaction, text : str):

        buf = io.BytesIO()

        img = Image.open(self._asset_path("hqdefault.png"))
        draw = ImageDraw.Draw(img)
        

        draw.text((90, 55), text, (255, 255, 255), font=self.font_minecraft)

        img.save(buf, format="PNG")
        buf.seek(0)

        await ctx.response.send_message(file=discord.File(buf, "image.png"))

    @app_commands.command(name="whiteboard", description="Write on a whiteboard")
    async def whiteboard(self, ctx : discord.Interaction, text : str):
        
        buf = io.BytesIO()

        img = Image.open(self._asset_path("Whiteboard.png"))
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
        
        img = Image.open(self._asset_path("rip.png"))
        draw = ImageDraw.Draw(img)
        draw.text((img.width//2, 399), content, (0, 0, 0), font=self.font_american_captain, anchor="mm")

        img.save(buf, format="PNG")
        buf.seek(0)

        await ctx.response.send_message(file=discord.File(buf, "image.png"))

async def setup(bot):
    await bot.add_cog(Images(bot))