
from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    import helper as helper_typing

import aiosqlite
import sqlite3
import json 
import os
import datetime

from setup import var

class HelperDatabase():
    def __init__(self, hc : helper_typing.HelperClient):
        self.connection : aiosqlite.Connection = None 
        self.hc = hc
        
        self.initialise_tables : list[str] = [
            "warns (id INTEGER PRIMARY KEY AUTOINCREMENT, guild INTEGER NOT NULL, user INTEGER NOT NULL, time TIMESTAMP NOT NULL, mod INTEGER NOT NULL, reason STRING)",
            "custom_commands (guild INTEGER, name STRING, value STRING)",
            "guildconfig_joinleave (guild INTEGER PRIMARY KEY, join_channel INTEGER, join_message STRING, leave_channel INTEGER, leave_message STRING)",
            "guildconfig_logging (guild INTEGER PRIMARY KEY, channel INTEGER, ignore STRING)",
            "guildconfig_autorole (guild INTEGER PRIMARY KEY, role INTEGER)",
            "events (guild INTEGER, amount INTEGER, what STRING, action STRING)",
            "balances (guild INTEGER, user INTEGER, balance INTEGER)",
            "flags_user (user INTEGER, flag_name STRING, flag_value INTEGER)",
            "flags_user_guild (user INTEGER, guild INTEGER, flag_name STRING, flag_value INTEGER)",
            "temp_nick_store (guild INTEGER, user INTEGER, nickname STRING, time TIMESTAMP)"
        ]
    
    async def execute(self, *args):
        return await self.connection.execute(*args)
    async def fetchone(self, *args):
        return await (await self.execute(*args)).fetchone()
    async def fetchall(self, *args):
        return await (await self.execute(*args)).fetchall()
    
    async def initialise(self):
        self.connection = await aiosqlite.connect(var.db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        

        for table_statement in self.initialise_tables:
            await self.connection.execute(f"CREATE TABLE IF NOT EXISTS " + table_statement)
    
    async def migrate_old(self):

        if os.path.exists("./databases/warns.json"):
            with open("databases/warns.json", encoding="utf-8") as f:
                d : dict = json.load(f)
                for guild_id_str, guild_warns in d.items():
                    for user_id_str, user_warns in guild_warns.items():
                        for warn in user_warns.values():
                            await self.connection.execute(
                                "INSERT INTO warns (guild, user, time, mod, reason) VALUES (?, ?, ?, ?, ?)", 
                                (int(guild_id_str), int(user_id_str), datetime.datetime.strptime(warn["time"], '%Y-%m-%d %H:%M:%S.%f'), int(warn["mod"]), warn.get("reason"))
                            )
            os.rename('databases/warns.json', 'databases/OLD_warns.json')
        
        if os.path.exists("./databases/commands.json"):
            with open("databases/commands.json", encoding="utf-8") as f:
                d : dict = json.load(f)

                for guild_id_str, commands in d.items():
                    for command_name, command_value in commands.items():
                        await self.connection.execute(
                            "INSERT INTO custom_commands VALUES (?, ?, ?)", 
                            (int(guild_id_str), command_name, command_value)
                        )
            os.rename('databases/commands.json', 'databases/OLD_commands.json')
        
        if os.path.exists("./databases/setup.json"):
            with open("databases/setup.json", encoding="utf-8") as f:
                d : dict = json.load(f)

                for guild_id_str, config in d.items():
                    if "join" in config or "leave" in config:
                        join = config.get("join") or {}
                        leave = config.get("leave") or {}
                        joinchannel = int(join.get("channel")) if join.get("channel") else None
                        leavechannel = int(leave.get("channel")) if leave.get("channel") else None

                        await self.execute("INSERT INTO guildconfig_joinleave VALUES (?, ?, ?, ?, ?)", (int(guild_id_str), joinchannel, join.get("message"), leavechannel, leave.get("message")))

                    if "logging" in config and config["logging"].get("channel"):
                        ignore = ",".join(list(config["logging"]["ignore"]))

                        await self.execute("INSERT INTO guildconfig_logging VALUES (?, ?, ?)", (int(guild_id_str), int(config["logging"]["channel"]), ignore))
                    if "autorole" in config and config["autorole"]:

                        await self.execute("INSERT INTO guildconfig_autorole VALUES (?, ?)", (int(guild_id_str), int(config["autorole"])))
        
            os.rename('databases/setup.json', 'databases/OLD_setup.json')
        
        if os.path.exists("./databases/events.json"):
            with open("databases/events.json", encoding="utf-8") as f:
                d : dict = json.load(f)

                for guild_id_str, events in d.items():
                    for event_raw in events:
                        await self.execute("INSERT INTO events VALUES (?, ?, ?, ?)", (int(guild_id_str), event_raw["amount"], event_raw["what"], event_raw["action"]))
        
            os.rename('databases/events.json', 'databases/OLD_events.json')
        
        if os.path.exists("./databases/economy.json"):
            with open("databases/economy.json", encoding="utf-8") as f:
                d : dict = json.load(f)

                for guild_id_str, users in d.items():
                    for user_id_str, data in users.items():
                        await self.execute("INSERT INTO balances VALUES (?, ?, ?)", (int(guild_id_str), int(user_id_str), data["balance"]))
        
            os.rename('databases/economy.json', 'databases/OLD_economy.json')
        
        if os.path.exists("./databases/userSettings.json"):
            with open("databases/userSettings.json", encoding="utf-8") as f:
                d : dict = json.load(f)

                for user_id_str, config in d.items():
                    for config_name, config_value in config.items():
                        if config_name == "data":
                            for flag_name, flag_value in config_value.items():
                                if flag_name == "mimicPrompt":
                                    flag_name = "mimic_prompt"
                                await self.execute("INSERT INTO flags_user VALUES (?, ?, ?)", (int(user_id_str), flag_name, int(flag_value)))
                        if config_name == "disableMimic":
                            for guild_id_str, flag_value in config_value.items():
                                if flag_value == True:
                                    await self.execute("INSERT INTO flags_user_guild VALUES (?, ?, 'disable_mimic', ?)", (int(user_id_str), int(guild_id_str), int(flag_value)))
        
            os.rename('databases/userSettings.json', 'databases/OLD_userSettings.json')

        await self.connection.commit()


