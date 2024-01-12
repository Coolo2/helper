
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
            "warns (id INTEGER PRIMARY KEY AUTOINCREMENT, guild INTEGER NOT NULL, user INTEGER NOT NULL, time TIMESTAMP NOT NULL, mod INTEGER NOT NULL, reason STRING)"
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
            with open("databases/warns.json") as f:
                d : dict = json.load(f)
                for guild_id_str, guild_warns in d.items():
                    for user_id_str, user_warns in guild_warns.items():
                        for warn in user_warns.values():
                            await self.connection.execute(
                                "INSERT INTO warns (guild, user, time, mod, reason) VALUES (?, ?, ?, ?, ?)", 
                                (int(guild_id_str), int(user_id_str), datetime.datetime.strptime(warn["time"], '%Y-%m-%d %H:%M:%S.%f'), int(warn["mod"]), warn.get("reason"))
                            )
            os.rename('databases/warns.json', 'databases/OLD_warns.json')

        await self.connection.commit()


