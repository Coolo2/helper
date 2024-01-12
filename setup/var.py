
import os
import discord

embed=0xFF8700
embedSuccess=0x00FF00
embedFail=0xFF0000

version = "a1.3.0"

address = "http://helperbot.ddns.net:35590"
port = 35590

client_id = 444882566529417216
client_secret = os.getenv("client_secret")
encryption_key = os.getenv("encryption_key")
invite = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=0&redirect_uri={address}/invited&response_type=code&scope=bot%20applications.commands"
login = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&redirect_uri={address}/login&response_type=code&scope=identify%20guilds"

dblToken = os.getenv("dblToken")

server = "https://discord.gg/HChmbSN"
topgg = "https://top.gg/bot/486180321444888586"

support_guild_add_remove_channel = 681410332832563234
support_guild_id = 447702058162978827

botAdmins = [368071242189897728, 444176530357354527, 378189620288159754]

db_path = ".db"

# Slash Commands
production = False
guilds = [discord.Object(450914634963353600)]
reload_slash_commands = False
reload_custom_commands = True

    