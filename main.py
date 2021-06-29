import discord, random, json, os, aiohttp, sys
from discord.ext import commands, tasks
from EasyConversion.textformat import color as c
from functions import functions
from setup import var
from webserver import main
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.members = True

def get_prefix(bot, message):
    try:
        with open('databases/prefixes.json') as f:
            prefixes = json.load(f)
        
        prefix = prefixes[str(message.guild.id)]
        return commands.when_mentioned_or(prefix, prefix.upper(), prefix.capitalize())(bot, message)
    except:
        return commands.when_mentioned_or(var.prefix, var.prefix.upper(), var.prefix.capitalize())(bot, message)

bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')

@bot.event 
async def on_ready():
    print(c.green + c.underline + bot.user.name + " online" + c.end)
    
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
    
    await functions.read_load("databases/prefixes.json")
    await functions.read_load("databases/userSettings.json")
    await functions.read_load("databases/commands.json")

if __name__ == '__main__':
    print(f'\n--- Extensions {", ".join(extensions)} ---')

    for extension in extensions:
        try:
            bot.load_extension('cogs.'+extension)
            print('{}Loaded {}{}'.format(c.green, 'cogs.'+extension, c.end))
        except Exception as error:
            print('{}{} cannot be loaded. [{}]{}'.format(c.red, 'cogs.'+extension, error, c.end))

    print('---\n ' + c.red)
    main.webserver_run(bot)

    bot.run(os.environ.get("token"))