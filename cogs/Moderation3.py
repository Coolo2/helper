import discord, random, os, json
from discord.ext import commands
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime, timedelta

class Moderation3(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="role", description="prefixrole [add/remove] [user/all] [rolename]|Add or remove roles from users")
    @commands.guild_only()
    async def role(self, ctx, setting = None, user = None, *, rolename = None):
        prefix = functions.prefix(ctx.guild)

        if setting == None or user == None or rolename == None:
            embed = discord.Embed(title="Help for {}role".format(prefix), color=var.embed)
            embed.add_field(name="What it does", value= "{}role - Add roles to a user or all users".format(prefix), inline = False)
            embed.add_field(name="Arguments", value= f"{prefix}role [add/remove] [user/all] [rolename]", inline = False)
            embed.add_field(name="Example", value= f"{prefix}role add all Member", inline = False)
            await ctx.send(embed=embed)
        else:
            if setting == "add":
                if user not in ["all", "everyone", "allmembers"]:
                    users = user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                    for member in ctx.guild.members:
                        if str(member.id) == users:
                            userobject = member
                    for role in ctx.guild.roles:
                        if role.name == rolename:
                            therole = role
                    try:
                        therole = therole 
                    except:
                        return await ctx.send("> Could not find role. Please input a valid role **name**")
                    if not ctx.author.guild_permissions.manage_roles or not ctx.author.top_role.position > therole.position and not ctx.guild.owner == ctx.author:
                        return await ctx.send("> You do not have permission to do this!")
                    try:
                        theuser = userobject
                    except Exception as error:
                        theuser = None
                        await ctx.send("> Could not find such user.")
                    if theuser != None:
                        try:
                            await userobject.add_roles(therole)
                            await ctx.send(f"> Successfully added role **{therole}** to **{userobject.name}**")
                        except Exception as error:
                            await ctx.send(f"> I do not have permission to add role {rolename}.")
                elif user in ["all", "everyone", "allmembers"]:
                    counter = 0
                    errors = 0
                    successful = 0
                    firsttime = round(int(len(ctx.guild.members)) / 5)
                    calculation = round(firsttime * 3.5)
                    for role in ctx.guild.roles:
                        if role.name == rolename:
                            therole = role
                    try:
                        therole = therole 
                    except:
                        return await ctx.send("> Could not find role. Please input a valid role **name**")
                    if not ctx.author.guild_permissions.manage_roles or not ctx.author.top_role.position > therole.position and not ctx.guild.owner == ctx.author:
                        return await ctx.send("> You do not have permission to do this!")
                    try:
                        await ctx.send(f"> Started adding role **{therole.name}** to all {len(ctx.guild.members)} members! This is estimated to take {calculation} seconds.")
                        goahead = 1
                    except:
                        await ctx.send(f"> Could not find role **{rolename}**!")        
                        goahead = 0
                    if goahead == 1:
                        for member in ctx.guild.members:
                            try:
                                await member.add_roles(therole)
                                successful = successful + 1
                            except Exception as error:
                                errors = errors + 1
                            counter = counter + 1
                            if counter == int(round(int(len(ctx.guild.members)) / 2)):
                                await ctx.send("> **50 percent done**")
                        embed = discord.Embed(title="Roles added to **{}** users!".format(str(counter)), colour=var.embed) 
                        embed.add_field(name="Information", value=f"Added role **{therole}** to **{successful}** users")
                        if errors == 0:
                            errors = "No errors 🎉"
                        else:
                            errors = f"Could not add role **{therole}** to **{errors}** users `Missing permissions`"
                        embed.add_field(name="Errors", value=errors)
                        await ctx.send(embed=embed)
            elif setting == "remove":
                if user in ["all", "everyone", "allmembers"]:
                    counter = 0
                    errors = 0
                    successful = 0
                    firsttime = round(int(len(ctx.guild.members)) / 5)
                    calculation = round(firsttime * 3.5)
                    for role in ctx.guild.roles:
                        if role.name == rolename:
                            therole = role
                    try:
                        therole = therole 
                    except:
                        return await ctx.send("> Could not find role. Please input a valid role **name**")
                    if not ctx.author.guild_permissions.manage_roles or not ctx.author.top_role.position > therole.position and not ctx.guild.owner == ctx.author:
                        return await ctx.send("> You do not have permission to do this!")
                    try:
                        await ctx.send(f"> Started removing role **{therole.name}** from all {len(ctx.guild.members)} members! This is estimated to take {calculation} seconds.")
                        goahead = 1
                    except:
                        await ctx.send(f"> I am missing permission to remove role {rolename}.")        
                        goahead = 0
                    if goahead == 1:
                        for member in ctx.guild.members:
                            try:
                                await member.remove_roles(therole)
                                successful = successful + 1
                            except Exception as error:
                                errors = errors + 1
                            counter = counter + 1
                            if counter == int(round(int(len(ctx.guild.members)) / 2)):
                                await ctx.send("> **50 percent done**")
                        embed = discord.Embed(title=f"Roles removed from **{counter}** users!", colour=var.embed) 
                        embed.add_field(name="Information", value=f"Removed role **{therole}** from **{successful}** users")
                        if errors == 0:
                            errors = "No errors 🎉"
                        else:
                            errors = f"Could not remove role **{therole}** from **{errors}** users `Missing permissions`"
                        embed.add_field(name="Errors", value=errors)
                        await ctx.send(embed=embed)
                else:
                    users = user.replace("<", "").replace(">", "").replace("@", "").replace("!", "")
                    for member in ctx.guild.members:
                        if str(member.id) == users:
                            userobject = member
                    for role in ctx.guild.roles:
                        if role.name == rolename:
                            therole = role
                    try:
                        therole = therole 
                    except:
                        return await ctx.send("> Could not find role. Please input a valid role **name**")
                    if not ctx.author.guild_permissions.manage_roles or not ctx.author.top_role.position > therole.position and not ctx.guild.owner == ctx.author:
                        return await ctx.send("> You do not have permission to do this!")

                    try:
                        theuser = userobject
                    except Exception as error:
                        theuser = None
                        await ctx.send("> Could not find such user.")
                    if theuser != None:
                        try:
                            await userobject.remove_roles(therole)
                            await ctx.send(f"> Successfully removed role **{therole}** from **{userobject.name}**")
                        except Exception as error:
                            await ctx.send(f"> I am missing permission to remove role {rolename}")
            else:
                embed = discord.Embed(title="Help for {}role".format(prefix), color=var.embed)
                embed.add_field(name="What it does", value= "{}role - Add roles to a user or all users".format(prefix), inline = False)
                embed.add_field(name="Arguments", value= f"{prefix}role [add/remove] [user/all] [rolename]", inline = False)
                embed.add_field(name="Example", value= f"{prefix}role add all Member", inline = False)
                await ctx.send(embed=embed)
    
    @commands.command(name="nick", description="prefixnick [user] [nickname/reset]|Change the nickname of a user", aliases=['nickname', 'setnick', 'setnickname'])
    @commands.guild_only()
    async def nick(self, ctx, object1, *, nickname = None):
        if object1 == None or nickname == None:
            prefix = functions.prefix(ctx.guild)
            embed = discord.Embed(title="Help for {}nick".format(prefix), color=var.embed)
            embed.add_field(name="What it does", value= "{}nick - Change the nickname of a user".format(prefix), inline = False)
            embed.add_field(name="Arguments", value= f"{prefix}nick [user/all] [nickname/reset]", inline = False)
            await ctx.send(embed=embed)
        else:
            if object1 != "all":
                for member in ctx.guild.members:
                    if str(member.id) in object1 or member.display_name == object1 or member.name == object1:
                        if ctx.message.author.guild_permissions.change_nickname and member == ctx.message.author:
                            doit=1
                        elif ctx.message.author.guild_permissions.manage_nicknames:
                            doit=1
                        else:
                            doit=0
                            await ctx.send("> An error has occurred: Missing `manage_nicknames` permission")
                        if doit == 1:
                            try:
                                if nickname == "reset":
                                    await member.edit(nick=member.name)
                                    await ctx.send(f"> Successfully reset **{member}**s nickname!")
                                else:
                                    await member.edit(nick=nickname)
                                    await ctx.send(f"> Successfully set **{member}**s nickname to **{nickname}**")
                            except:
                                await ctx.send("> Could not change nickname `Bot Missing permissions`")
            else:
                if ctx.message.author.guild_permissions.manage_nicknames:
                    counter = 0
                    errors = 0
                    successful = 0
                    firsttime = round(int(len(ctx.guild.members)) / 5)
                    calculation = round(firsttime * 3.5)

                    if nickname != "reset":
                        await ctx.send(f"> Started changing {len(ctx.guild.members)} nicknames to {nickname}. This is estimated to take {calculation} seconds.")
                    else:
                        await ctx.send(f"> Started resetting {len(ctx.guild.members)} nicknames. This is estimated to take {str(calculation)} seconds.")

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