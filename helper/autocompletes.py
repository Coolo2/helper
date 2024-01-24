
import discord 
from discord import app_commands

import helper

async def commands_autocomplete(interaction : discord.Interaction, current : str):
    return [app_commands.Choice(name=f"/{command.qualified_name}", value=command.qualified_name) for command in interaction.client.tree.walk_commands() if current in f"/{command.qualified_name}" and type(command) != app_commands.Group and not command.extras.get("IGNORE_IN_COMMAND_LISTS")][:25]

async def command_category_autocomplete(interaction : discord.Interaction, current : str):

    hc : helper.HelperClient = interaction.client.hc
    categories : list[str] = []

    for command in hc.bot.tree.walk_commands():
        category_name = helper.utils.category_name_from_cog_name(command.module)
        if category_name not in categories and current.lower() in category_name.lower():
            categories.append(category_name)
    return [app_commands.Choice(name=c.title(), value=c.title()) for c in categories]