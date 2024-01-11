
from setup import var
import discord

class MainEmbed(discord.Embed):
    def __init__(self, title : str = None, description : str = None):
        super().__init__(title=title, description=description, color=var.embed)

class FailEmbed(discord.Embed):
    def __init__(self, title : str = None, description : str = None):
        super().__init__(title=title, description=description, color=var.embedFail)

class SuccessEmbed(discord.Embed):
    def __init__(self, title : str = None, description : str = None):
        super().__init__(title=title, description=description, color=var.embedSuccess)