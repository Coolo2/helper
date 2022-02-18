from EasyConversion.textformat import color as c
import discord
from setup import var
from functions import customCommands
import json
import sys




def on_connect_overwrite_sync(bot : discord.Bot, guild_id = int):

    async def on_connect_overwrite():

        pass

    
    return on_connect_overwrite

async def invoke_autocomplete_callback(self, ctx: discord.AutocompleteContext) -> None:
    option = ctx.interaction.data["options"][0]
    command = discord.utils.find(lambda x: x.name == option["name"], self.subcommands)
    ctx.interaction.data = option
    try:
        await command.invoke_autocomplete_callback(ctx)
    except Exception as e:
        print(e)

def register_commands_update(bot : discord.Bot):

    async def register_commands() -> None:
        """|coro|
        Registers all commands that have been added through :meth:`.add_application_command`.
        This method cleans up all commands over the API and should sync them with the internal cache of commands.
        This will only be rolled out to Discord if :meth:`.http.get_global_commands` has certain keys that differ from :data:`.pending_application_commands`
        By default, this coroutine is called inside the :func:`.on_connect`
        event. If you choose to override the :func:`.on_connect` event, then
        you should invoke this coroutine as well.
        .. versionadded:: 2.0
        """
        commands_to_bulk = []

        needs_bulk = False

        # Global Command Permissions
        global_permissions = []

        registered_commands = await bot.http.get_global_commands(bot.user.id)
        # 'Your app cannot have two global commands with the same name. Your app cannot have two guild commands within the same name on the same guild.'
        # We can therefore safely use the name of the command in our global slash commands as a unique identifier
        registered_commands_dict = {cmd["name"]:cmd for cmd in registered_commands}
        global_pending_application_commands_dict = {}
        
        for command in [
            cmd for cmd in bot.pending_application_commands if cmd.guild_ids is None
        ]:
            as_dict = command.to_dict()
            
            global_pending_application_commands_dict[command.name] = as_dict
            if command.name in registered_commands_dict:
                match = registered_commands_dict[command.name]
            else:
                match = None
            # TODO: There is probably a far more efficient way of doing this
            # We want to check if the registered global command on Discord servers matches the given global commands
            if match:
                as_dict["id"] = match["id"]

                keys_to_check = {"default_permission": True, "name": True, "description": True, "options": ["type", "name", "description", "autocomplete", "choices"]}
                for key, more_keys in {
                    key:more_keys
                    for key, more_keys in keys_to_check.items()
                    if key in as_dict.keys()
                    if key in match.keys()
                }.items():
                    if key == "options":
                        for i, option_dict in enumerate(as_dict[key]):
                            if command.name == "recent":
                                print(option_dict, "|||||", match[key][i])
                            for key2 in more_keys:
                                pendingVal = None
                                if key2 in option_dict.keys():
                                    pendingVal = option_dict[key2]
                                    if pendingVal == False or pendingVal == []: # Registered commands are not available if choices is an empty array or if autocomplete is false
                                        pendingVal = None
                                matchVal = None
                                if key2 in match[key][i].keys():
                                    matchVal = match[key][i][key2]
                                    if matchVal == False or matchVal == []: # Registered commands are not available if choices is an empty array or if autocomplete is false
                                        matchVal = None

                                if pendingVal != matchVal:
                                    # When a property in the options of a pending global command is changed
                                    needs_bulk = True
                    else:
                        if as_dict[key] != match[key]:
                            # When a property in a pending global command is changed
                            needs_bulk = True
            else:
                # When a name of a pending global command is not registered in Discord
                needs_bulk = True

            commands_to_bulk.append(as_dict)
        
        for name, command in registered_commands_dict.items():
            if not name in global_pending_application_commands_dict.keys():
                # When a registered global command is not available in the pending global commands
                needs_bulk = True
    
        if needs_bulk:
            commands = await bot.http.bulk_upsert_global_commands(bot.user.id, commands_to_bulk)
        else:
            commands = registered_commands

        for i in commands:
            cmd = discord.utils.get(
                bot.pending_application_commands,
                name=i["name"],
                guild_ids=None,
                type=i["type"],
            )
            if cmd:
                cmd.id = i["id"]
                bot._application_commands[cmd.id] = cmd

                # Permissions (Roles will be converted to IDs just before Upsert for Global Commands)
                global_permissions.append({"id": i["id"], "permissions": cmd.permissions})

        update_guild_commands = {}
        async for guild in bot.fetch_guilds(limit=None):
            update_guild_commands[guild.id] = []
        for command in [
            cmd
            for cmd in bot.pending_application_commands
            if cmd.guild_ids is not None
        ]:
            as_dict = command.to_dict()
            for guild_id in command.guild_ids:
                to_update = update_guild_commands[guild_id]
                update_guild_commands[guild_id] = to_update + [as_dict]

        for guild_id, guild_data in update_guild_commands.items():
            try:
                commands = await bot.http.bulk_upsert_guild_commands(
                    bot.user.id, guild_id, update_guild_commands[guild_id]
                )

                # Permissions for this Guild
                guild_permissions = []
            except:
                if not guild_data:
                    continue
                print(f"Failed to add command to guild {guild_id}", file=sys.stderr)
                raise
            else:
                for i in commands:
                    cmd = discord.utils.find(lambda cmd: cmd.name == i["name"] and cmd.type == i["type"] and int(i["guild_id"]) in cmd.guild_ids, bot.pending_application_commands)
                    cmd.id = i["id"]
                    bot._application_commands[cmd.id] = cmd

                    # Permissions
                    permissions = [
                        perm.to_dict()
                        for perm in cmd.permissions
                        if perm.guild_id is None
                        or (
                            perm.guild_id == guild_id and perm.guild_id in cmd.guild_ids
                        )
                    ]
                    guild_permissions.append(
                        {"id": i["id"], "permissions": permissions}
                    )

                for global_command in global_permissions:
                    permissions = [
                        perm.to_dict()
                        for perm in global_command["permissions"]
                        if perm.guild_id is None
                        or (
                            perm.guild_id == guild_id and perm.guild_id in cmd.guild_ids
                        )
                    ]
                    guild_permissions.append(
                        {"id": global_command["id"], "permissions": permissions}
                    )

                # Collect & Upsert Permissions for Each Guild
                # Command Permissions for this Guild
                guild_cmd_perms = []

                # Loop through Commands Permissions available for this Guild
                for item in guild_permissions:
                    new_cmd_perm = {"id": item["id"], "permissions": []}

                    # Replace Role / Owner Names with IDs
                    for permission in item["permissions"]:
                        if isinstance(permission["id"], str):
                            # Replace Role Names
                            if permission["type"] == 1:
                                role = discord.utils.get(
                                    bot.get_guild(guild_id).roles,
                                    name=permission["id"],
                                )

                                # If not missing
                                if role is not None:
                                    new_cmd_perm["permissions"].append(
                                        {
                                            "id": role.id,
                                            "type": 1,
                                            "permission": permission["permission"],
                                        }
                                    )
                                else:
                                    print(
                                        "No Role ID found in Guild ({guild_id}) for Role ({role})".format(
                                            guild_id=guild_id, role=permission["id"]
                                        )
                                    )
                            # Add owner IDs
                            elif (
                                permission["type"] == 2 and permission["id"] == "owner"
                            ):
                                app = await bot.application_info()  # type: ignore
                                if app.team:
                                    for m in app.team.members:
                                        new_cmd_perm["permissions"].append(
                                            {
                                                "id": m.id,
                                                "type": 2,
                                                "permission": permission["permission"],
                                            }
                                        )
                                else:
                                    new_cmd_perm["permissions"].append(
                                        {
                                            "id": app.owner.id,
                                            "type": 2,
                                            "permission": permission["permission"],
                                        }
                                    )
                        # Add the rest
                        else:
                            new_cmd_perm["permissions"].append(permission)

                    # Make sure we don't have over 10 overwrites
                    if len(new_cmd_perm["permissions"]) > 10:
                        print(
                            "Command '{name}' has more than 10 permission overrides in guild ({guild_id}).\nwill only use the first 10 permission overrides.".format(
                                name=bot._application_commands[new_cmd_perm["id"]].name,
                                guild_id=guild_id,
                            )
                        )
                        new_cmd_perm["permissions"] = new_cmd_perm["permissions"][:10]

                    # Append to guild_cmd_perms
                    guild_cmd_perms.append(new_cmd_perm)

                # Upsert
                try:
                    await bot.http.bulk_upsert_command_permissions(
                        bot.user.id, guild_id, guild_cmd_perms
                    )
                except discord.Forbidden:
                    print(
                        f"Failed to add command permissions to guild {guild_id}",
                        file=sys.stderr,
                    )
                    raise
    
    return register_commands
