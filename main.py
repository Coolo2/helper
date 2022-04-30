from discord.ext import commands, tasks 
import discord
import asyncio

import json, os
from EasyConversion.textformat import color as c
from functions import functions, customCommands
from setup import var
from webserver import main
from datetime import datetime

intents = discord.Intents.default()
intents.members = True

def get_prefix(bot, message):
    try:
        with open('databases/prefixes.json') as f:
            prefixes = json.load(f)
        
        prefix = prefixes[str(message.guild.id)]
        return commands.when_mentioned_or(prefix, prefix.upper(), prefix.capitalize())(bot, message)
    except Exception as e:
        return commands.when_mentioned_or(var.prefix, var.prefix.upper(), var.prefix.capitalize())(bot, message)

bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents, debug_guilds=[447702058162978827])

extensions = [file.replace(".py", "") for file in os.listdir('./cogs') if file.endswith(".py")]

@bot.event 
async def on_ready():
    print(c.green + c.underline + bot.user.name + " online" + c.end)

    var.get_client(bot)
    
    await bot.change_presence(activity=discord.Game(name=f"/help | v{var.version} | {len(bot.guilds)} servers"))
    ping_files.start()

    if var.reload_slash_commands:
        if var.production:
            await tree.sync()
        else:
            for guild in var.guilds:
                await tree.sync(guild=guild)

    #await customCommands.sync_custom_commands(bot)

@tasks.loop(seconds=10)
async def ping_files():
    data = await functions.read_data('databases/mutes.json')
    for guild in data:
        for member in data[guild]:
            if data[guild][member]["endAt"] != None:
                if (datetime.now() - datetime.strptime(data[guild][member]["endAt"], "%d-%b-%Y (%H:%M:%S.%f)")).total_seconds() > 0:
                    await functions.unmute(bot.get_guild(int(guild)), bot.get_guild(int(guild)).get_member(int(member)))
    
    read_load_items = ["prefixes", "userSettings", "commands", "setup"]

    for file_name in read_load_items:

        await asyncio.sleep(1)
        await functions.read_load(f"databases/{file_name}.json")

@bot.check
async def globally_blacklist_roles(ctx):
    with open('databases/blacklist.json') as f:
        prefixes = json.load(f)
    blacklist = prefixes  # Role names
    return not str(ctx.author.id) in blacklist

#extensions.remove("Handling1")

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
    main.webserver_run(bot)

    

bot.setup_hook = setup_hook

bot.run(os.getenv("token"))
    