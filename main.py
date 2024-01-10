from discord.ext import commands 
import discord

import os
from EasyConversion.textformat import color as c
from setup import var
from webserver import main
import helper

from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.default()
intents.members = True

bot : discord.Client = commands.Bot(command_prefix=commands.when_mentioned, case_insensitive=True, intents=intents, debug_guilds=[447702058162978827])
hc = helper.HelperClient()

hc.bot = bot 
bot.hc = hc

extensions = [file.replace(".py", "") for file in os.listdir('./cogs') if file.endswith(".py")]

@bot.event 
async def on_ready():
    print(c.green + c.underline + bot.user.name + " online" + c.end)
    
    await bot.change_presence(activity=discord.CustomActivity(name=f"{var.version} | {len(bot.guilds)} servers | /changelog"))

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
        await bot.tree.sync()
    
    for g in var.guilds: 
        await bot.tree.sync(guild=g)
    await bot.tree.sync(guild=discord.Object(var.support_guild_id))
        
    app = main.generate_app(bot, hc)
    bot.loop.create_task(app.run_task(host="0.0.0.0", port=var.port, debug=False))

bot.setup_hook = setup_hook

bot.run(os.getenv("token"))
    