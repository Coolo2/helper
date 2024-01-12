
from helper import errors, styling, utils, autocompletes, types, database
from discord.ext import commands


class HelperClient():
    def __init__(self):
        self.bot : commands.Bot = None
        self.db = database.HelperDatabase(self)
    
