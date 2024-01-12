from discord.ext import commands 
import discord

import json, os
from setup import var
import asyncio, aiohttp, requests
from datetime import datetime, timedelta
from urllib.parse import urlparse
from difflib import SequenceMatcher

from functions import components
import helper

import re

def format_html_basic(text : str):
    replaced = text.replace("<b>", "**").replace("</b>", "**").replace("<i>", "*").replace("</i>", "*").replace("<code>", "`").replace("</code>", "`").replace("<u>", "__").replace("</u>", "__")
    return re.compile("<.*?>").sub("", replaced)

def get_bot_users(bot):
    servers = list(bot.guilds)
    counter = 0
    for x in range(len(servers)):
        server = servers[x-1]
        counter = counter + len(server.members)
    return counter

def oneTime(timeStr):
    if "y" in timeStr:
        return int(timeStr.replace("y", "")) * 86400 * 365
    if "m" in timeStr:
        return int(timeStr.replace("m", "")) * 86400 * 30
    if "w" in timeStr:
        return int(timeStr.replace("w", "")) * 86400 * 7
    if "d" in timeStr:
        return int(timeStr.replace("d", "")) * 86400
    if "h" in timeStr:
        return int(timeStr.replace("h", "")) * 3600
    if "m" in timeStr:
        return int(timeStr.replace("m", "")) * 60
    if "s" in timeStr:
        return int(timeStr.replace("s", ""))

    return int(timeStr)

def timeToSeconds(timeStr):
    timeStr = timeStr.lower()
    returnTime = 0
    if " " in timeStr:
        for time in timeStr.split(" "):
            returnTime += oneTime(time)
        return returnTime

    return oneTime(timeStr)

def time_str_from_seconds(time):
    timeSeconds = time
    day = timeSeconds // (24 * 3600)
    timeSeconds = timeSeconds % (24 * 3600)
    hour = timeSeconds // 3600
    timeSeconds %= 3600
    minutes = timeSeconds // 60
    timeSeconds %= 60
    seconds = timeSeconds

    day = f" {round(day)}d" if day != 0 else ""
    hour = f" {round(hour)}h" if hour != 0 else ""
    minutes = f" {round(minutes)}m" if minutes != 0 else ""

    if day == "" and hour == "" and minutes == "":
        return f"{round(seconds)}s"
    
    return f"{day}{hour}{minutes}".lstrip()



async def check_events(hc : helper.HelperClient, guild : discord.Guild, member : discord.Member, warn_count : int = None):

    events = await read_data("databases/events.json")

    if warn_count == None:
        warn_count = (await hc.db.fetchone("SELECT COUNT(*) FROM warns WHERE guild=? AND user=?", (guild.id, member.id)))[0]
    
    if str(guild.id) not in events:
        return 
    
    for event in events[str(guild.id)]:
        if event["what"] == "warns":
            if warn_count == int(event["amount"]):

                if event["action"] == "1hTimeout":
                    return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=1)), helper.types.EventType.timeout, "1 Hour Timeout")
                if event["action"] == "3hTimeout":
                    return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=3)), helper.types.EventType.timeout, "3 Hour Timeout")
                if event["action"] == "6hTimeout":
                    return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=6)), helper.types.EventType.timeout, "6 Hour Timeout")
                if event["action"] == "12hTimeout":
                    return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=12)), helper.types.EventType.timeout, "12 Hour Timeout")
                if event["action"] == "24hTimeout":
                    return components.EventConfirmationButton(member, member.timeout_for(timedelta(hours=24)), helper.types.EventType.timeout, "24 Hour Timeout")
                if event["action"] == "kick":
                    return components.EventConfirmationButton(member, member.kick(reason=str(warn_count) + " warns"), helper.types.EventType.kick, "Kick")
                if event["action"] == "ban":
                    return components.EventConfirmationButton(member, member.ban(reason=str(warn_count) + " warns"), helper.types.EventType.kick, "Ban")
    return None


async def is_url_image(image_url, image_formats):
    if "http" not in str(image_url):
        return False
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as r:
                if r.headers["content-type"] in image_formats:
                    return True
                return False
    except Exception as e:
        return False

async def imageFromArg(ctx : discord.Interaction, args, imgTuple, imgList):
    imgURL = ""
    
    if args != None and await is_url_image(args, imgTuple):
        imgURL = args
    elif args != None and True in [True if member.name.lower() == args.lower() 
        or member.display_name.lower() == args.lower() 
        or str(member.id) == args 
        or member.mention.replace("!", "") == args.replace("!", "") else False for member in ctx.guild.members]:

        for member in ctx.guild.members:
            if member.name.lower() == args.lower() or member.display_name.lower() == args.lower() or str(member.id) == args or member.mention.replace("!", "") == args.replace("!", ""):
                imgURL = member.avatar.url if member.avatar else None
    else:
        imgURL = ctx.user.avatar.url if ctx.user.avatar else None
    if imgURL == "":
        return False
    return imgURL

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
    with open(fileName, encoding="utf-8") as f:
        return json.load(f)
    #async with aiohttp.ClientSession() as session:
    #    async with session.get(f"http://helperdata.glitch.me/view{os.getenv('databaseToken')}/{fileName}") as r:
    #        jsond = await r.json()
    #        return jsond

def read_data_sync(fileName):
    with open(fileName, encoding="utf-8") as f:
        return json.load(f)
    #r = requests.get(f"http://helperdata.glitch.me/view{os.getenv('databaseToken')}/{fileName}")
    #return r.json()


async def save_data(fileName, data):
    with open(fileName, "w", encoding="utf-8") as f:
        json.dump(data, f)
        return data
    #async with aiohttp.ClientSession() as session:
    #    async with session.post(f"http://helperdata.glitch.me/save{os.getenv('databaseToken')}/{fileName}", data={'data':json.dumps(data)}) as r:
    #        return json.loads(await r.text())

def save_data_sync(fileName, data):
    with open(fileName, "w", encoding="utf-8") as f:
        json.dump(data, f)
        return data
    #r = requests.post(f"http://helperdata.glitch.me/save{os.getenv('databaseToken')}/{fileName}", data={'data':json.dumps(data)})
    #return json.loads(r.text)

async def read_load(where, data=None):
    if data == None:
        data = await read_data(where)
    with open(where, 'w') as f:
        json.dump(data, f)

def read_load_sync(where, data=None):
    if data == None:
        data = read_data_sync(where)
    with open(where, 'w') as f:
        json.dump(data, f)

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc, result.path])
    except Exception as e:
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

def calculateTime(argument):
    if "h" in argument:
        return str(int(argument.replace("h", "").replace(" ", "").replace(":", "").replace(",", "")) * 3600)
    if "m" in argument:
        return str(int(argument.replace("m", "").replace(" ", "").replace(":", "").replace(",", "")) * 60)
    if "s" in argument:
        return argument.replace("s", "").replace(" ", "").replace(":", "").replace(",", "")

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
            except Exception as e:
                return command
    return None

async def log(bot : commands.Bot, type : str, guild : discord.Guild, embed : discord.Embed):
    with open("databases/setup.json") as f:
        data = json.load(f)
    
    try:
        ignore = data[str(guild.id)]["logging"]["ignore"]
        if type not in ignore:
            logChannel = guild.get_channel(int(data[str(guild.id)]["logging"]["channel"]))

            await logChannel.send(embed=embed)
    except Exception as e:
        pass