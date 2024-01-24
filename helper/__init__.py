
from helper import errors, styling, utils, autocompletes, types, database, paginator
from discord.ext import commands
from discord import app_commands


class HelperClient():
    def __init__(self):
        self.bot : commands.Bot = None
        self.db = database.HelperDatabase(self)
    
    @property 
    def commands_list(self) -> list[app_commands.Command]:
        return [command for command in self.bot.tree.walk_commands() if not command.extras.get("IGNORE_IN_COMMAND_LISTS") and type(command) != app_commands.Group]
    
