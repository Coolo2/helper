from discord.ext import commands 
import discord

import json
from setup import var
import helper

from discord import app_commands

class Moderation2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hc : helper.HelperClient = bot.hc
    
    @app_commands.command(name="role", description="Add or remove roles from users")
    @app_commands.guild_only()
    @app_commands.describe(setting="Add or remove role", user="The user to add or remove the role to. Can be 'all'", role="The role to add or remove")
    @app_commands.choices(setting=[app_commands.Choice(name="Add", value="add"), app_commands.Choice(name="Remove", value="remove")])
    async def role(
        self, 
        ctx : discord.Interaction, 
        setting : str, 
        user : str, 
        role : discord.Role
    ):

        if setting == "add":
            if user not in ["all", "everyone", "allmembers"]:
                users = user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                for member in ctx.guild.members:
                    if str(member.id) == users:
                        userobject = member

                if not ctx.user.guild_permissions.manage_roles or not ctx.user.top_role.position > role.position and not ctx.guild.owner == ctx.user:
                    return await ctx.response.send_message("> You do not have permission to do this!")
                try:
                    theuser = userobject
                except Exception as error:
                    theuser = None
                    return await ctx.response.send_message("> Could not find such user.")
                if theuser != None:
                    try:
                        await userobject.add_roles(role)
                        return await ctx.response.send_message(f"> Successfully added role **{role}** to **{userobject.name}**")
                    except Exception as error:
                        return await ctx.response.send_message(f"> I do not have permission to add role {role}.")
            elif user in ["all", "everyone", "allmembers"]:
                counter = 0
                errors = 0
                successful = 0
                firsttime = round(int(len(ctx.guild.members)) / 5)
                calculation = round(firsttime * 3.5)

                if not ctx.user.guild_permissions.manage_roles or not ctx.user.top_role.position > role.position and not ctx.guild.owner == ctx.user:
                    return await ctx.response.send_message("> You do not have permission to do this!")
                try:
                    await ctx.response.send_message(f"> Started adding role **{role.name}** to all {len(ctx.guild.members)} members! This is estimated to take {calculation} seconds.")
                    goahead = 1
                except Exception as e:
                    await ctx.response.send_message(f"> Could not find role **{role}**!")        
                    goahead = 0

                if goahead == 1:
                    for member in ctx.guild.members:
                        try:
                            await member.add_roles(role)
                            successful = successful + 1
                        except Exception as error:
                            errors = errors + 1
                        counter = counter + 1
                        if counter == int(round(int(len(ctx.guild.members)) / 2)):
                            await ctx.channel.send("> **50 percent done**")
                    embed = discord.Embed(title="Roles added to **{}** users!".format(str(counter)), colour=var.embed) 
                    embed.add_field(name="Information", value=f"Added role **{role}** to **{successful}** users")
                    if errors == 0:
                        errors = "No errors 🎉"
                    else:
                        errors = f"Could not add role **{role}** to **{errors}** users `Missing permissions`"
                    embed.add_field(name="Errors", value=errors)
                    await ctx.channel.send(embed=embed)
        elif setting == "remove":
            if user in ["all", "everyone", "allmembers"]:
                counter = 0
                errors = 0
                successful = 0
                firsttime = round(int(len(ctx.guild.members)) / 5)
                calculation = round(firsttime * 3.5)

                if not ctx.user.guild_permissions.manage_roles or not ctx.user.top_role.position > role.position and not ctx.guild.owner == ctx.user:
                    return await ctx.response.send_message("> You do not have permission to do this!")
                try:
                    await ctx.response.send_message(f"> Started removing role **{role.name}** from all {len(ctx.guild.members)} members! This is estimated to take {calculation} seconds.")
                    goahead = 1
                except Exception as e:
                    await ctx.response.send_message(f"> I am missing permission to remove role {role}.")        
                    goahead = 0
                if goahead == 1:
                    for member in ctx.guild.members:
                        try:
                            await member.remove_roles(role)
                            successful = successful + 1
                        except Exception as error:
                            errors = errors + 1
                        counter = counter + 1
                        if counter == int(round(int(len(ctx.guild.members)) / 2)):
                            await ctx.channel.send("> **50 percent done**")
                    embed = discord.Embed(title=f"Roles removed from **{counter}** users!", colour=var.embed) 
                    embed.add_field(name="Information", value=f"Removed role **{role}** from **{successful}** users")
                    if errors == 0:
                        errors = "No errors 🎉"
                    else:
                        errors = f"Could not remove role **{role}** from **{errors}** users `Missing permissions`"
                    embed.add_field(name="Errors", value=errors)
                    await ctx.channel.send(embed=embed)
            else:
                users = user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                for member in ctx.guild.members:
                    if str(member.id) == users:
                        userobject = member

                if not ctx.user.guild_permissions.manage_roles or not ctx.user.top_role.position > role.position and not ctx.guild.owner == ctx.user:
                    return await ctx.response.send_message("> You do not have permission to do this!")

                try:
                    theuser = userobject
                except Exception as error:
                    theuser = None
                    await ctx.response.send_message("> Could not find such user.")
                if theuser != None:
                    try:
                        await userobject.remove_roles(role)
                        await ctx.response.send_message(f"> Successfully removed role **{role}** from **{userobject.name}**")
                    except Exception as error:
                        await ctx.response.send_message(f"> I am missing permission to remove role {role}")
    
    @app_commands.command(name="nickname", description="Change the nickname of a user")
    @app_commands.guild_only()
    @app_commands.describe(user="The user to change the nickname of. Can also be 'all'", nickname="The nickname to change to. Can be 'reset'")
    async def nick(
        self, 
        ctx : discord.Interaction, 
        user : str, 
        nickname : str
    ):

        if user != "all":
            for member in ctx.guild.members:
                if str(member.id) in user or member.display_name == user or member.name == user:
                    if ctx.user.guild_permissions.change_nickname and member == ctx.user:
                        doit=1
                    elif ctx.user.guild_permissions.manage_nicknames:
                        doit=1
                    else:
                        doit=0
                        await ctx.response.send_message("> An error has occurred: Missing `manage_nicknames` permission")
                    if doit == 1:
                        try:
                            if nickname == "reset":
                                await member.edit(nick=member.name)
                                await ctx.response.send_message(f"> Successfully reset **{member}**s nickname!")
                            else:
                                await member.edit(nick=nickname)
                                await ctx.response.send_message(f"> Successfully set **{member}**s nickname to **{nickname}**")
                        except Exception as e:
                            await ctx.response.send_message("> Could not change nickname `Bot Missing permissions`")
        else:
            if ctx.user.guild_permissions.manage_nicknames:
                counter = 0
                errors = 0
                successful = 0
                firsttime = round(int(len(ctx.guild.members)) / 5)
                calculation = round(firsttime * 3.5)

                if nickname != "reset":
                    await ctx.response.send_message(f"> Started changing {len(ctx.guild.members)} nicknames to {nickname}. This is estimated to take {calculation} seconds.")
                else:
                    await ctx.response.send_message(f"> Started resetting {len(ctx.guild.members)} nicknames. This is estimated to take {str(calculation)} seconds.")

                for member in ctx.guild.members:
                    try:
                        previous_nickname = await self.hc.db.fetchone("SELECT nickname FROM temp_nick_store WHERE guild=? AND user=?", (ctx.guild.id, member.id))

                        if nickname == "reset":
                            await member.edit(nick=previous_nickname[0] if previous_nickname else None)
                        else:
                            
                            if not previous_nickname:
                                await self.hc.db.execute("INSERT INTO temp_nick_store VALUES (?, ?, ?, CURRENT_TIMESTAMP)", (ctx.guild.id, member.id, member.display_name))
                            await member.edit(nick=nickname)
                        successful = successful + 1
                    except Exception as error:
                        errors = errors + 1
                    
                    counter = counter + 1
                    if counter == int(round(int(len(ctx.guild.members)) / 2)):
                        await ctx.channel.send("> **50 percent done**")
                if nickname == "reset":
                    await self.hc.db.execute("DELETE FROM temp_nick_store WHERE guild=?", (ctx.guild.id,))
                
                if errors == 0:
                    errors = "No errors 🎉"
                else:
                    errors = f"Could not set nickname **{nickname}** for **{errors}** users `Missing permissions`"

                embed = helper.styling.MainEmbed(f"Nickname set for **{counter}** users!", (f"Set nickname to {nickname} for {successful} users" if nickname != "reset" else f"Reset {successful} user's nicknames") + f"\n\n{errors}") 
                
                await ctx.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation2(bot))