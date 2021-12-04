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
load_dotenv('.env')

intents = discord.Intents.default()
intents.members = True
intents.messages=False

#utility1

def get_prefix(bot, message):
    try:
        with open('databases/prefixes.json') as f:
            prefixes = json.load(f)
        
        prefix = prefixes[str(message.guild.id)]
        return commands.when_mentioned_or(prefix, prefix.upper(), prefix.capitalize())(bot, message)
    except:
        return commands.when_mentioned_or(var.prefix, var.prefix.upper(), var.prefix.capitalize())(bot, message)

#bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
bot = discord.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents, debug_guild=var.guilds[0])
#bot.remove_command('help')

customCommands.loadCustomCommands(bot)

@bot.event 
async def on_ready():
    

    print(c.green + c.underline + bot.user.name + " online" + c.end)

    var.get_client(bot)
    
    await bot.change_presence(activity=discord.Game(name=f"@{bot.user.name} help | v{var.version} | {len(bot.guilds)} servers"))
    ping_files.start()

extensions = [file.replace(".py", "") for file in os.listdir('./cogs') if file.endswith(".py")]

@tasks.loop(seconds=10)
async def ping_files():
    data = await functions.read_data('databases/mutes.json')
    for guild in data:
        for member in data[guild]:
            if data[guild][member]["endAt"] != None:
                if (datetime.now() - datetime.strptime(data[guild][member]["endAt"], "%d-%b-%Y (%H:%M:%S.%f)")).total_seconds() > 0:
                    await functions.unmute(bot.get_guild(int(guild)), bot.get_guild(int(guild)).get_member(int(member)))
    
    await asyncio.sleep(1)
    await functions.read_load("databases/prefixes.json")
    await asyncio.sleep(1)
    await functions.read_load("databases/userSettings.json")
    await asyncio.sleep(1)
    await functions.read_load("databases/commands.json")
    await asyncio.sleep(1)
    await functions.read_load("databases/joinleave.json")

@bot.check
async def globally_blacklist_roles(ctx):
    with open('databases/blacklist.json') as f:
        prefixes = json.load(f)
    blacklist = prefixes  # Role names
    return not str(ctx.author.id) in blacklist


if __name__ == '__main__':
    print(f'\n--- Extensions {", ".join(extensions)} ---')

    for extension in extensions:
        try:
            bot.load_extension('cogs.'+ extension)

            print('{}Loaded {}{}'.format(c.green, 'cogs.'+extension, c.end))
        except Exception as error:
            print('{}{} cannot be loaded. [{}]{}'.format(c.red, 'cogs.'+extension, error, c.end))

    print('---\n ' + c.red)
    main.webserver_run(bot)
    

    bot.run(os.environ.get("token"))