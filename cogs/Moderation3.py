from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime, timedelta

from discord.commands import slash_command, Option

class Moderation3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @slash_command(name="role", description="Add or remove roles from users")
    @commands.guild_only()
    async def role(
        self, 
        ctx, 
        setting : Option(str, description="Add or remove role", choices=["add", "remove"]), 
        user : Option(str, description="User or 'all' - User(s) to add the role to"), 
        role : Option(discord.Role, description="The role to add / remove")
    ):

        if setting == "add":
            if user not in ["all", "everyone", "allmembers"]:
                users = user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                for member in ctx.guild.members:
                    if str(member.id) == users:
                        userobject = member

                if not ctx.author.guild_permissions.manage_roles or not ctx.author.top_role.position > role.position and not ctx.guild.owner == ctx.author:
                    return await ctx.respond("> You do not have permission to do this!")
                try:
                    theuser = userobject
                except Exception as error:
                    theuser = None
                    return await ctx.respond("> Could not find such user.")
                if theuser != None:
                    try:
                        await userobject.add_roles(role)
                        return await ctx.respond(f"> Successfully added role **{role}** to **{userobject.name}**")
                    except Exception as error:
                        return await ctx.respond(f"> I do not have permission to add role {role}.")
            elif user in ["all", "everyone", "allmembers"]:
                counter = 0
                errors = 0
                successful = 0
                firsttime = round(int(len(ctx.guild.members)) / 5)
                calculation = round(firsttime * 3.5)

                if not ctx.author.guild_permissions.manage_roles or not ctx.author.top_role.position > role.position and not ctx.guild.owner == ctx.author:
                    return await ctx.respond("> You do not have permission to do this!")
                try:
                    await ctx.respond(f"> Started adding role **{role.name}** to all {len(ctx.guild.members)} members! This is estimated to take {calculation} seconds.")
                    goahead = 1
                except:
                    await ctx.respond(f"> Could not find role **{role}**!")        
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
                            await ctx.send("> **50 percent done**")
                    embed = discord.Embed(title="Roles added to **{}** users!".format(str(counter)), colour=var.embed) 
                    embed.add_field(name="Information", value=f"Added role **{role}** to **{successful}** users")
                    if errors == 0:
                        errors = "No errors 🎉"
                    else:
                        errors = f"Could not add role **{role}** to **{errors}** users `Missing permissions`"
                    embed.add_field(name="Errors", value=errors)
                    await ctx.send(embed=embed)
        elif setting == "remove":
            if user in ["all", "everyone", "allmembers"]:
                counter = 0
                errors = 0
                successful = 0
                firsttime = round(int(len(ctx.guild.members)) / 5)
                calculation = round(firsttime * 3.5)

                if not ctx.author.guild_permissions.manage_roles or not ctx.author.top_role.position > role.position and not ctx.guild.owner == ctx.author:
                    return await ctx.respond("> You do not have permission to do this!")
                try:
                    await ctx.respond(f"> Started removing role **{role.name}** from all {len(ctx.guild.members)} members! This is estimated to take {calculation} seconds.")
                    goahead = 1
                except:
                    await ctx.respond(f"> I am missing permission to remove role {role}.")        
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
                            await ctx.send("> **50 percent done**")
                    embed = discord.Embed(title=f"Roles removed from **{counter}** users!", colour=var.embed) 
                    embed.add_field(name="Information", value=f"Removed role **{role}** from **{successful}** users")
                    if errors == 0:
                        errors = "No errors 🎉"
                    else:
                        errors = f"Could not remove role **{role}** from **{errors}** users `Missing permissions`"
                    embed.add_field(name="Errors", value=errors)
                    await ctx.send(embed=embed)
            else:
                users = user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                for member in ctx.guild.members:
                    if str(member.id) == users:
                        userobject = member

                if not ctx.author.guild_permissions.manage_roles or not ctx.author.top_role.position > role.position and not ctx.guild.owner == ctx.author:
                    return await ctx.respond("> You do not have permission to do this!")

                try:
                    theuser = userobject
                except Exception as error:
                    theuser = None
                    await ctx.respond("> Could not find such user.")
                if theuser != None:
                    try:
                        await userobject.remove_roles(role)
                        await ctx.respond(f"> Successfully removed role **{role}** from **{userobject.name}**")
                    except Exception as error:
                        await ctx.respond(f"> I am missing permission to remove role {role}")
    
    @slash_command(name="nick", description="Change the nickname of a user", aliases=['nickname', 'setnick', 'setnickname'])
    @commands.guild_only()
    async def nick(
        self, 
        ctx, 
        object1 : Option(str, name="user", description="The user to change the nickname of. Can also be 'all'"), 
        nickname : Option(str, description="The nickname to change to. Set to 'reset' to reset.")
    ):
        if object1 != "all":
            for member in ctx.guild.members:
                if str(member.id) in object1 or member.display_name == object1 or member.name == object1:
                    if ctx.author.guild_permissions.change_nickname and member == ctx.author:
                        doit=1
                    elif ctx.author.guild_permissions.manage_nicknames:
                        doit=1
                    else:
                        doit=0
                        await ctx.respond("> An error has occurred: Missing `manage_nicknames` permission")
                    if doit == 1:
                        try:
                            if nickname == "reset":
                                await member.edit(nick=member.name)
                                await ctx.respond(f"> Successfully reset **{member}**s nickname!")
                            else:
                                await member.respond(nick=nickname)
                                await ctx.respond(f"> Successfully set **{member}**s nickname to **{nickname}**")
                        except:
                            await ctx.respond("> Could not change nickname `Bot Missing permissions`")
        else:
            if ctx.author.guild_permissions.manage_nicknames:
                counter = 0
                errors = 0
                successful = 0
                firsttime = round(int(len(ctx.guild.members)) / 5)
                calculation = round(firsttime * 3.5)

                if nickname != "reset":
                    await ctx.respond(f"> Started changing {len(ctx.guild.members)} nicknames to {nickname}. This is estimated to take {calculation} seconds.")
                else:
                    await ctx.respond(f"> Started resetting {len(ctx.guild.members)} nicknames. This is estimated to take {str(calculation)} seconds.")

                data = {}
                
                with open("databases/nicks.json") as f:
                    prefixes = json.load(f)

                for member in ctx.guild.members:
                    try:
                        try:
                            if str(member.id) in prefixes[str(ctx.guild.id)]:
                                pass 
                            else:
                                data[str(member.id)] = member.display_name
                        except:
                            data[str(member.id)] = member.display_name
                        if nickname == "reset":
                            try:
                                prev = prefixes[str(ctx.guild.id)][str(member.id)]
                            except:
                                prev = member.name
                            await member.edit(nick=prev)
                        else:
                            await member.edit(nick=nickname)
                        successful = successful + 1


                    except Exception as error:
                        errors = errors + 1
                    counter = counter + 1
                    if counter == int(round(int(len(ctx.guild.members)) / 2)):
                        await ctx.send("> **50 percent done**")
                if nickname == "reset":
                    data = "none"

                try:
                    if str(ctx.guild.id) in prefixes:
                        if prefixes[str(ctx.guild.id)] != "none":
                            if nickname == "reset":
                                prefixes[str(ctx.guild.id)] = data
                                doit=1
                            else:
                                doit = 0
                        else:
                            prefixes[str(ctx.guild.id)] = data
                            doit =1
                    else:
                        prefixes[str(ctx.guild.id)] = data
                        doit = 1
                except:
                    prefixes[str(ctx.guild.id)] = data
                    doit = 1
                if doit == 1:
                    with open("databases/nicks.json", "w") as f:
                        json.dump(prefixes, f)
                embed = discord.Embed(title=f"Nickname set for **{counter}** users!", 
                    description=f"Set nickname to {nickname} for {successful} users" if nickname != "reset" else f"Reset {successful} user's nicknames", colour=var.embed) 
                if errors == 0:
                    errors = "No errors 🎉"
                else:
                    errors = f"Could not set nickname **{nickname}** for **{errors}** users `Missing permissions`"
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Moderation3(bot))