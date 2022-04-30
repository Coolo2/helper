from discord.ext import commands 
import discord

import random, os, json
from setup import var
from functions import customerror
from functions import functions
from datetime import datetime

from discord import app_commands

class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member to warn", reason="A reason to show for the warn")
    async def warn(
        self, 
        ctx : discord.Interaction, 
        member: discord.Member, 
        reason : str = "None"
    ):
        await ctx.response.defer()
        data = await functions.read_data("databases/warns.json")

        thedate = str(datetime.now())
        if str(ctx.guild.id) not in data:
            data[str(ctx.guild.id)] = {}
        if str(member.id) not in data[str(ctx.guild.id)]:
            data[str(ctx.guild.id)][str(member.id)] = {}

        for i in range(1, 1000):
            if str(i) not in data[str(ctx.guild.id)][str(member.id)]:
                warnID = str(i)
                break

        data[str(ctx.guild.id)][str(member.id)][warnID] = {
            "time":thedate,
            "mod":str(ctx.user.id),
            "reason":reason
        }
        
        data = await functions.save_data("databases/warns.json", data)

        button = await functions.check_events(self.bot, data, ctx.guild, member)
        noArg = f"\n\n__Top tip!__ Add a warn reason with `{functions.prefix(ctx.guild)}warn [user] [reason]`!"

        view = discord.ui.View()
        view.timeout = 600
        if button:
            view.add_item(button)

        try:
            memberEmbed = discord.Embed(
                title=random.choice(["Uh oh!", "Oops!", "Oh no!"]),
                description=f"You have been warned in **{ctx.guild.name}** for: **{reason}**" + (f". You may also be given a **{button.name}**." if button != None else ""),
                color=var.embedFail
            )
            await member.send(embed=memberEmbed)
            embed = discord.Embed(
                title=random.choice([f"Successfully warned {member.display_name}", "Successfully warned!", f"Warned {member.display_name} successfully!"]),
                description=f"Warned **{member.display_name}** successfully with reason: **{reason}**" + (f". Due to your [Server Events]({var.address}/dashboard#{ctx.guild.id}), this user should now get a **{button.name}**. Use the button below to do this action." if button != None else "") + (noArg if reason == "None" else ""),
                colour=var.embedSuccess
            )
        except Exception as e:
            embed = discord.Embed(
                title=random.choice([f"Successfully warned {member.display_name}", "Successfully warned!", f"Warned {member.display_name} successfully!"]),
                description=f"Warned **{member.display_name}** successfully with reason: **{reason}**, however could not DM them." + (f". Due to your [Server Events]({var.address}/dashboard#{ctx.guild.id}), this user should now get a **{button.name}**. Use the button below to do this action." if button != None else "") + (noArg if reason == "None" else ""),
                colour=var.embedSuccess
            )
        embed.add_field(name="Warn ID", value=len(data[str(ctx.guild.id)][str(member.id)]))
        embed.add_field(name="Moderator", value=str(ctx.user))
        embed.set_footer(text=f"{member.display_name} now has {len(data[str(ctx.guild.id)][str(member.id)])} warn(s)")
        await ctx.followup.send(embed=embed, view=view)

        # Log update if available
        embed = discord.Embed(title="User warned", color=var.embed, timestamp=datetime.now())
        embed.add_field(name="User:", value=str(member), inline=False)
        embed.add_field(name="Reason:", value=str(reason), inline=False)
        embed.add_field(name="Moderator", value=str(ctx.user))
        embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

        await functions.log(self.bot, "warns", ctx.guild, embed)
    
    @app_commands.command(name="warns", description="Check a users warns")
    @app_commands.guild_only()
    @app_commands.describe(member="Member to get warns for")
    async def warns(self, ctx : discord.Interaction, member: discord.Member):
        if member == None:
            member = ctx.user
        data = await functions.read_data("databases/warns.json")
        embedNone = discord.Embed(
            title=random.choice([f"Found no warns for {member.display_name}", f"{member.display_name} has no warns"]),
            description=f"Could not find any warns for **{member.display_name}** :tada:", 
            colour=var.embed
        )
        if str(ctx.guild.id) not in data:
            return await ctx.response.send_message(embed=embedNone)
        elif str(member.id) not in data[str(ctx.guild.id)]:
            return await ctx.response.send_message(embed=embedNone)
        
        embed = discord.Embed(
                title=random.choice([f"Found warns for {member.display_name}", f"{member.display_name}'s warns"]),
                description=f"Here {'is' if len(data[str(ctx.guild.id)][str(member.id)]) == 1 else 'are'} the **{len(data[str(ctx.guild.id)][str(member.id)])}** warn{'' if len(data[str(ctx.guild.id)][str(member.id)]) == 1 else 's'} I found for **{member.display_name}**", 
                colour=var.embed
        )

        for warn in data[str(ctx.guild.id)][str(member.id)]:

            f_date = datetime.strptime(data[str(ctx.guild.id)][str(member.id)][warn]['time'], '%Y-%m-%d %H:%M:%S.%f')
            l_date = datetime.now()
            delta = l_date - f_date

            embed.add_field(
                name=f"ID: {warn} - Moderator: {self.bot.get_user(int(data[str(ctx.guild.id)][str(member.id)][warn]['mod']))} - {str(delta.days)} day{'' if delta.days == 1 else 's'} ago", 
                value=data[str(ctx.guild.id)][str(member.id)][warn]["reason"], 
                inline=False
            )
        return await ctx.response.send_message(embed=embed)
    
    @app_commands.command(name="delwarn", description="Delete a warn from a user")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member to delete a warn for", warnid="The warn ID to remove (can be 'all')")
    async def delwarn(
        self, 
        ctx : discord.Interaction, 
        member: discord.Member,
        warnid : str
    ):
        data = await functions.read_data("databases/warns.json")
        embedNone = discord.Embed(
            title=random.choice([f"Found no warns for {member.display_name}", f"{member.display_name} has no warns"]),
            description=f"Could not find any warns for **{member.display_name}**", 
            colour=var.embedFail
        )
        embedNo = discord.Embed(
            title=random.choice([f"Could not find warn ID {warnid}", f"Could not find a warn with ID {warnid}"]),
            description=f"Could not find any warns for **{member.display_name}** with warn ID **{warnid}**", 
            colour=var.embedFail
        )
        embedAll = discord.Embed(
            title=random.choice([f"Deleted all warns for {member.display_name}", f"Deleted all of {member.display_name}'s warns"]),
            description=f"Deleted all warns for **{member.display_name}**", 
            colour=var.embedSuccess
        )
        embed = discord.Embed(
            title=random.choice([f"Deleted warn ID **{warnid}**", f"Deleted {member.display_name}'s warn"]),
            description=f"Deleted warn with ID **{warnid}** for **{member.display_name}**", 
            colour=var.embedSuccess
        )
        if str(ctx.guild.id) not in data:
            return await ctx.response.send_message(embed=embedNone)
        elif str(member.id) not in data[str(ctx.guild.id)]:
            return await ctx.response.send_message(embed=embedNone)
        elif warnid == "all":
            wrns = []
            for warn in data[str(ctx.guild.id)][str(member.id)]:
                wrns.append(warn)
            for warn in wrns:
                del data[str(ctx.guild.id)][str(member.id)][warn]
            await ctx.response.send_message(embed=embedAll)
        elif warnid not in data[str(ctx.guild.id)][str(member.id)]:
            return await ctx.response.send_message(embed=embedNo)
        else:
            del data[str(ctx.guild.id)][str(member.id)][warnid]
            await ctx.response.send_message(embed=embed)

        if len(data[str(ctx.guild.id)][str(member.id)]) == 0:
            del data[str(ctx.guild.id)][str(member.id)]
        if len(data[str(ctx.guild.id)]) == 0:
            del data[str(ctx.guild.id)]

        await functions.save_data("databases/warns.json", data)

        # Log update if available
        embed = discord.Embed(title="Warn deleted", color=var.embedFail, timestamp=datetime.now())
        embed.add_field(name="User:", value=str(member), inline=False)
        embed.add_field(name="Moderator", value=str(ctx.user))
        embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

        await functions.log(self.bot, "warns", ctx.guild, embed)
    
    

async def setup(bot):
    await bot.add_cog(Warns(bot), guilds=var.guilds)