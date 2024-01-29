from discord.ext import commands, tasks
import discord

import os
from EasyConversion.textformat import color as c
from setup import var
from webserver import main
import helper
import datetime

from functions import customCommands

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

@tasks.loop(seconds=5 if var.production else 30)
async def _commit_db():
    await hc.db.execute("DELETE FROM temp_nick_store WHERE time<?", (datetime.datetime.now()-datetime.timedelta(days=45),))
    await hc.db.connection.commit()

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
        await bot.tree.sync(guild=discord.Object(var.support_guild_id))
        bot.loop.create_task(customCommands.sync_custom_commands(hc))
    
    await hc.db.initialise()
    await hc.db.migrate_old()
    _commit_db.start()

    app = main.generate_app(bot, hc)
    bot.loop.create_task(app.run_task(host="0.0.0.0", port=var.port, debug=False))

bot.setup_hook = setup_hook

bot.run(os.getenv("token"))
    