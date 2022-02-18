import typing
import discord 

from functions import classes

class EventConfirmationButton(discord.ui.Button):

    def __init__(self, member : discord.Member, coro : typing.Coroutine, eventType : classes.EventType, name : str):

        self.member = member 
        self.coro = coro 
        self.eventType = eventType
        self.name = name 

        super().__init__(label=name, style=discord.ButtonStyle.primary)
    
    async def callback(self, interaction : discord.Interaction):

        if interaction.user.guild_permissions.manage_messages:
            await self.coro 

            return await interaction.response.send_message(f"Successfully given **{self.member}** a **{self.name}**", allowed_mentions=discord.AllowedMentions.none())
        else:
            return await interaction.response.send_message("You do not have sufficient permissions to do this.", ephemeral=True)
