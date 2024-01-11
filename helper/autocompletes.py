
import discord 
from discord import app_commands

async def commands_autocomplete(interaction : discord.Interaction, current : str):
    return [app_commands.Choice(name=f"/{command.qualified_name}", value=command.qualified_name) for command in interaction.client.tree.walk_commands() if current in f"/{command.qualified_name}" and type(command) != app_commands.Group and not command.extras.get("IGNORE_IN_COMMAND_LISTS")][:25]