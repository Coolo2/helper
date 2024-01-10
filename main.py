from discord.ext import commands, tasks 
import discord
import asyncio

import json, os
from EasyConversion.textformat import color as c
from functions import functions, customCommands
from setup import var
from webserver import main
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.


intents = discord.Intents.default()
intents.members = True

bot : discord.Client = commands.Bot(command_prefix=commands.when_mentioned, case_insensitive=True, intents=intents, debug_guilds=[447702058162978827])

extensions = [file.replace(".py", "") for file in os.listdir('./cogs') if file.endswith(".py")]

@bot.event 
async def on_ready():
    print(c.green + c.underline + bot.user.name + " online" + c.end)
    
    await bot.change_presence(activity=discord.Game(name=f"/help | {var.version} | {len(bot.guilds)} servers"))
    
    for g in var.guilds:
        await tree.sync(guild=g)

    #await customCommands.sync_custom_commands(bot)
    await tree.sync(guild=discord.Object(var.support_guild_id))

tree : discord.app_commands.CommandTree = bot.tree

async def setup_hook():
    print(f'\n--- Extensions {", ".join(extensions)} ---')

    for extension in extensions:
        try:

            await bot.load_extension('cogs.'+ extension)

            print('{}Loaded {}{}'.format(c.green, 'cogs.'+extension, c.end))
        except Exception as error:
            
            print('{}{} cannot be loaded. [{}]{}'.format(c.red, 'cogs.'+extension, error, c.end))

    print('---\n ' + c.red)
    if var.reload_slash_commands:
        await tree.sync()
        
    main.webserver_run(bot)

    

bot.setup_hook = setup_hook

bot.run(os.getenv("token"))
    