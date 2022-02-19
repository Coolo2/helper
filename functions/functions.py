from discord.ext import commands 
import discord

import json, os
from setup import var
import asyncio, aiohttp, requests
from datetime import datetime, timedelta
from urllib.parse import urlparse
from difflib import SequenceMatcher

from functions import components, classes

def get_bot_users(bot):
    servers = list(bot.guilds)
    counter = 0
    for x in range(len(servers)):
        server = servers[x-1]
        counter = counter + len(server.members)
    return counter

def prefix(guild):
    try:
        with open('databases/prefixes.json') as f:
            prefixes = json.load(f)
            return prefixes[str(guild.id)]
    except:
        theprefix = var.prefix
        return theprefix

def oneTime(timeStr):
    if "y" in timeStr:
        return int(timeStr.replace("y", "")) * 86400 * 365
    elif "m" in timeStr:
        return int(timeStr.replace("m", "")) * 86400 * 30
    elif "w" in timeStr:
        return int(timeStr.replace("w", "")) * 86400 * 7
    elif "d" in timeStr:
        return int(timeStr.replace("d", "")) * 86400
    elif "h" in timeStr:
        return int(timeStr.replace("h", "")) * 3600
    elif "m" in timeStr:
        return int(timeStr.replace("m", "")) * 60
    elif "s" in timeStr:
        return int(timeStr.replace("s", ""))
    else:
        return int(timeStr)

def timeToSeconds(timeStr):
    timeStr = timeStr.lower()
    returnTime = 0
    if " " in timeStr:
        for time in timeStr.split(" "):
            returnTime += oneTime(time)
        return returnTime
    else:
        return oneTime(timeStr)

async def unmute(guild, member : discord.Member):
    data = await read_data('databases/mutes.json')
    embed = discord.Embed(title="Successfully unmuted", description=f"Successfully unmuted **{member.display_name}**", colour=var.embedSuccess)
    for role in member.roles:
        if role.name == "Muted":
            await member.remove_roles(role)
            if str(guild.id) in data:
                if str(member.id) in data[str(guild.id)]:
                    for roleStr in data[str(guild.id)][str(member.id)]["roles"]:
                        try:
                            await member.add_roles(guild.get_role(int(roleStr)))
                        except Exception as e:
                            print(e)
                    del data[str(guild.id)][str(member.id)]
                else:
                    embed.add_field(name="Error", value=f"However, couldn't find previous roles for **{member.display_name}**")
            else:
                embed.add_field(name="Error", value=f"However, couldn't find previous roles for **{member.display_name}**")
    await save_data('databases/mutes.json', data)
    return embed

async def mute (bot, guild, member : discord.Member, length):
    errors = ""

    data = await read_data('databases/mutes.json')

    if member == guild.owner:
        embed = discord.Embed(title="Uh oh!", description="I can't mute the owner of the server", colour=var.embedFail)
        return embed
    elif member == bot.user:
        embed = discord.Embed(title="Uh oh!", description="I can't mute myself", colour=var.embedFail)
        return embed
    hasMuted = False
    for role in guild.roles:
        if role.name == "Muted":
            hasMuted = True
            mutedRole = role
    for role in member.roles:
        if role.name == "Muted":
            embed = discord.Embed(title="Uh oh!", description=f"**{member.display_name}** is already muted", colour=var.embedFail)
            return embed
    
    lengthOld = length
    if length != None:
        try:
            length = str((datetime.now() + timedelta(seconds=timeToSeconds(length))).strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        except:
            embed = discord.Embed(title="Uh oh!", description=f"Invalid mute length! Mute Length example: '2h 5m'", colour=var.embedFail)
            return embed
    
    embed = discord.Embed(title="Muted successfully", description=f"Successfully muted **{member.display_name}** " + f"for **{lengthOld}**" if lengthOld != None else "", colour=var.embedSuccess)

    if not hasMuted:

        mutedRole = await guild.create_role(name="Muted")

        for channel in guild.text_channels:
            try:
                await channel.set_permissions(mutedRole, send_messages=False, add_reactions=False)
                errors = errors + "true"
            except Exception as error:
                errors = errors + "false"
        for category in guild.categories:
            try:
                await category.set_permissions(mutedRole, send_messages=False, add_reactions=False)
                errors = errors + "true"
            except Exception as error:
                errors = errors + "false"
        
        if "true" not in errors:
            embed = discord.Embed(title="Uh oh!", description="I am missing manage_channels permissions.", colour=var.embedFail)
            return embed 
    rolelist = []
    for memberRole in member.roles:
        if memberRole.name == '@everyone':
            pass
        else:
            rolelist.append(str(memberRole.id))
        try:
            await member.remove_roles(memberRole)
            errors = errors + "true"
        except:
            errors = errors + "false"
    errors = errors.count("false")
    await member.add_roles(mutedRole)
    if str(guild.id) not in data:
        data[str(guild.id)] = {}
    data[str(guild.id)][str(member.id)] = {
        "roles":rolelist,
        "endAt":length
    }
    await save_data('databases/mutes.json', data)
    embed.add_field(name="Errors", value=f"{errors-1} errors")
    return embed

async def check_events(bot : discord.Bot, warns : dict, guild : discord.Guild, member : discord.Member):

    events = await read_data("databases/events.json")
    
    if str(guild.id) not in events:
        return 
    
    if str(guild.id) in warns:
        if str(member.id) in warns[str(guild.id)]:
            for event in events[str(guild.id)]:
                if event["what"] == "warns":
                    if len(warns[str(guild.id)][str(member.id)]) == int(event["amount"]):

                        if event["action"] == "1hMute":
                            return components.EventConfirmationButton(member, mute(bot, guild, member, "1h"), classes.EventType.mute, "1 Hour Mute")
                        if event["action"] == "3hMute":
                            return components.EventConfirmationButton(member, mute(bot, guild, member, "3h"), classes.EventType.mute, "3 Hour Mute")
                        if event["action"] == "6hMute":
                            return components.EventConfirmationButton(member, mute(bot, guild, member, "6h"), classes.EventType.mute, "6 Hour Mute")
                        if event["action"] == "12hMute":
                            return components.EventConfirmationButton(member, mute(bot, guild, member, "12h"), classes.EventType.mute, "12 Hour Mute")
                        if event["action"] == "24hMute":
                            return components.EventConfirmationButton(member, mute(bot, guild, member, "24h"), classes.EventType.mute, "24 Hour Mute")
                        if event["action"] == "1hTimeout":
                            return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=1)), classes.EventType.timeout, "1 Hour Timeout")
                        if event["action"] == "3hTimeout":
                            return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=3)), classes.EventType.timeout, "3 Hour Timeout")
                        if event["action"] == "6hTimeout":
                            return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=6)), classes.EventType.timeout, "6 Hour Timeout")
                        if event["action"] == "12hTimeout":
                            return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=12)), classes.EventType.timeout, "12 Hour Timeout")
                        if event["action"] == "24hTimeout":
                            return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=24)), classes.EventType.timeout, "24 Hour Timeout")
                        if event["action"] == "kick":
                            return components.EventConfirmationButton(member, member.kick(reason=str(len(warns[str(guild.id)][str(member.id)])) + " warns"), classes.EventType.kick, "Kick")
                        if event["action"] == "ban":
                            return components.EventConfirmationButton(member, member.ban(reason=str(len(warns[str(guild.id)][str(member.id)])) + " warns"), classes.EventType.kick, "Ban")
    return None


async def is_url_image(image_url, image_formats):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as r:
                if r.headers["content-type"] in image_formats:
                    return True
                return False
    except:
        return False

async def imageFromArg(ctx, args, imgTuple, imgList):
    imgURL = ""
    
    if args != None and await is_url_image(args, imgTuple):
        imgURL = args
    elif args != None and True in [True if member.name.lower() == args.lower() 
        or member.display_name.lower() == args.lower() 
        or str(member.id) == args 
        or member.mention == args else False for member in ctx.guild.members]:

        for member in ctx.guild.members:
            if member.name.lower() == args.lower() or member.display_name.lower() == args.lower() or str(member.id) == args or member.mention == args:
                imgURL = member.avatar.url if member.avatar else None
    else:
        imgURL = ctx.author.avatar.url if ctx.author.avatar else None
    if imgURL == "":
        return False
    return imgURL

    """elif message.attachments != [] and message.attachments[0].url.split(".")[-1].lower() in imgList:
        imgURL = message.attachments[0].url """

def replaceMessage(member, message):
    message = message.replace("{user}", member.name)
    message = message.replace("{member}", member.name)

    message = message.replace("{@user}", member.mention)
    message = message.replace("{@member}", member.mention)

    message = message.replace("{guild}", member.guild.name)
    message = message.replace("{server}", member.guild.name)

    message = message.replace("{guildMembers}", str(len(member.guild.members)))
    message = message.replace("{serverMembers}", str(len(member.guild.members)))
    return message

async def read_data(fileName):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://helperdata.glitch.me/view{os.getenv('databaseToken')}/{fileName}") as r:
            json = await r.json()
            return json

def read_data_sync(fileName):
    r = requests.get(f"http://helperdata.glitch.me/view{os.getenv('databaseToken')}/{fileName}")
    return r.json()


async def save_data(fileName, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://helperdata.glitch.me/save{os.getenv('databaseToken')}/{fileName}", data={'data':json.dumps(data)}) as r:
            return json.loads(await r.text())

def save_data_sync(fileName, data):
    r = requests.post(f"http://helperdata.glitch.me/save{os.getenv('databaseToken')}/{fileName}", data={'data':json.dumps(data)})
    return json.loads(r.text)

async def read_load(where, data=None):
    if data == None:
        data = await read_data(where)
    with open(where, 'w') as f:
        json.dump(data, f, indent=4)

def read_load_sync(where, data=None):
    if data == None:
        data = read_data_sync(where)
    with open(where, 'w') as f:
        json.dump(data, f, indent=4)

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

def colorfromword(input):
    if input.lower() == "blue":
        return 0x0000FF
    elif input.lower() == "red":
        return 0xFF0000
    elif input.lower() == "green":
        return 0x00FF00
    elif input.lower() == "purple":
        return 0x7D3C98
    elif input.lower() == "black":
        return 0x000000
    elif input.lower() == "white":
        return 0xFFFFFF
    elif input.lower() == "gray":
        return 0x808080
    elif input.lower() == "silver":
        return 0xC0C0C0
    elif input.lower() == "yellow":
        return 0xFFFF00
    elif input.lower() == "orange":
        return 0xFFA500  
    else:
        return ["orange", "yellow", "silver", "gray", "white", "black", "purple", "green", "red", "blue"]

def calculateTime(argument):
    if "h" in argument:
        return str(int(argument.replace("h", "").replace(" ", "").replace(":", "").replace(",", "")) * 3600)
    if "m" in argument:
        return str(int(argument.replace("m", "").replace(" ", "").replace(":", "").replace(",", "")) * 60)
    if "s" in argument:
        return argument.replace("s", "").replace(" ", "").replace(":", "").replace(",", "")

def changelog():
    with open("resources/changelog.txt") as f:
        return f.read()

def fuzzy_search(search_key, text, strictness):
    lines = text.split("\n")
    for i, line in enumerate(lines):
        words = line.split()
        for word in words:
            similarity = SequenceMatcher(None, word, search_key)
            if similarity.ratio() > strictness:
                return "*h"

def checkList(iterable, check):
    for command in iterable:
        det = fuzzy_search(str(command), check, 0.8)
        if det != None:
            try:
                return command.name
            except:
                return command
    return None

async def log(bot : discord.Bot, type : str, guild : discord.Guild, embed : discord.Embed):
    with open("databases/setup.json") as f:
        data = json.load(f)
    
    try:
        ignore = data[str(guild.id)]["logging"]["ignore"]
        if type not in ignore:
            logChannel = guild.get_channel(int(data[str(guild.id)]["logging"]["channel"]))

            await logChannel.send(embed=embed)
    except:
        pass