from discord.ext import commands 
import discord

import random
from setup import var
from functions import functions
from datetime import datetime, timedelta

from discord import app_commands

import helper

class Warns(commands.Cog):
    def __init__(self, bot, hc : helper.HelperClient):
        self.bot = bot
        self.hc = hc
    
    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member to warn", reason="A reason to show for the warn")
    async def warn(
        self, 
        interaction : discord.Interaction, 
        member: discord.Member, 
        reason : str = None
    ):

        await self.hc.db.execute("INSERT INTO warns (guild, user, time, mod, reason) VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?)", (interaction.guild.id, member.id, interaction.user.id, reason))
        id = (await self.hc.db.fetchone("SELECT MAX(id) FROM warns"))[0]
        warn_count = (await self.hc.db.fetchone("SELECT COUNT(*) FROM warns WHERE guild=? AND user=?", (interaction.guild.id, member.id)))[0]

        button = await functions.check_events(self.hc, interaction.guild, member, warn_count)
        noArg = f"\n\n__Top tip!__ Add a warn reason with `/warn [user] [reason]`!"

        view = discord.ui.View()
        view.timeout = 600
        if button:
            view.add_item(button)

        try:
            memberEmbed = discord.Embed(
                title=random.choice(["Uh oh!", "Oops!", "Oh no!"]),
                description=f"You have been warned in **{interaction.guild.name}** for: **{reason}**" + (f". You may also be given a **{button.name}**." if button != None else ""),
                color=var.embedFail
            )
            await member.send(embed=memberEmbed)
            embed = discord.Embed(
                title=random.choice([f"Successfully warned {member.display_name}", "Successfully warned!", f"Warned {member.display_name} successfully!"]),
                description=f"Warned **{member.display_name}** successfully with reason: **{reason}**" + (f". Due to your [Server Events]({var.address}/dashboard#{interaction.guild.id}), this user should now get a **{button.name}**. Use the button below to do this action." if button != None else "") + (noArg if reason == "None" else ""),
                colour=var.embedSuccess
            )
        except Exception as e:
            embed = discord.Embed(
                title=random.choice([f"Successfully warned {member.display_name}", "Successfully warned!", f"Warned {member.display_name} successfully!"]),
                description=f"Warned **{member.display_name}** successfully with reason: **{reason}**, however could not DM them." + (f". Due to your [Server Events]({var.address}/dashboard#{interaction.guild.id}), this user should now get a **{button.name}**. Use the button below to do this action." if button != None else "") + (noArg if reason == "None" else ""),
                colour=var.embedSuccess
            )
        embed.add_field(name="Warn ID", value=str(id))
        embed.add_field(name="Moderator", value=str(interaction.user))
        embed.set_footer(text=f"{member.display_name} now has {warn_count} warn(s)")
        await interaction.response.send_message(embed=embed, view=view)

        # Log update if available
        embed = discord.Embed(title="User warned", description=f"{member} now has {warn_count} warns", color=var.embed, timestamp=datetime.now())
        embed.add_field(name="User:", value=str(member), inline=False)
        embed.add_field(name="Reason:", value=str(reason), inline=False)
        embed.add_field(name="Moderator", value=str(interaction.user))
        embed.add_field(name="Warn ID", value=str(id), inline=False)
        embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

        await functions.log(self.hc, "warns", interaction.guild, embed)
    
    @app_commands.command(name="warns", description="Check a users warns")
    @app_commands.guild_only()
    @app_commands.describe(member="Member to get warns for")
    async def warns(self, interaction : discord.Interaction, member: discord.Member = None):
        if member == None:
            member = interaction.user
        
        warns_raw = await self.hc.db.fetchall("SELECT id, time, mod, reason FROM warns WHERE user=? AND guild=?", (member.id, interaction.guild.id))

        embedNone = discord.Embed(
            title=random.choice([f"Found no warns for {member.display_name}", f"{member.display_name} has no warns"]),
            description=f"Could not find any warns for **{member.display_name}** :tada:", 
            colour=var.embed
        )
        if len(warns_raw) == 0:
            return await interaction.response.send_message(embed=embedNone)
        
        embed = discord.Embed(
                title=random.choice([f"Found warns for {member.display_name}", f"{member.display_name}'s warns"]),
                description=f"Here {'is' if len(warns_raw) == 1 else 'are'} the **{len(warns_raw) }** warn{'' if len(warns_raw)  == 1 else 's'} I found for **{member.display_name}**", 
                colour=var.embed
        )

        for warn in warns_raw:
            embed.add_field(
                name=f"ID: {warn[0]} - Moderator: {self.bot.get_user(warn[2])} - <t:{int(warn[1].timestamp())}:R>", 
                value=f"Reason: {warn[3] or '*no reason provided*'}", 
                inline=False
            )
        return await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="warn_remove", description="Delete a warn from a user")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.describe(member="The member to delete a warn for", warnid="The warn ID to remove (can be 'all')")
    async def delwarn(
        self, 
        interaction : discord.Interaction, 
        member: discord.Member,
        warnid : str
    ):

        warns_exist = await self.hc.db.fetchone("SELECT COUNT(*) FROM warns WHERE guild=? AND user=?", (interaction.guild.id, member.id))

        if not warns_exist:
            raise helper.errors.MildErr(f"Could not find any warns for **{member.display_name}**")

        if warnid.isnumeric():
            embed = helper.styling.SuccessEmbed(f"Deleted {member.display_name}'s warn", f"Deleted warn with ID **{warnid}** for **{member.display_name}**")

            warn_raw = await self.hc.db.fetchone("SELECT id FROM warns WHERE guild=? AND user=? AND id=?", (interaction.guild.id, member.id, int(warnid)))

            if warn_raw == None:
                raise helper.errors.MildErr(f"Could not find any warns for **{member.display_name}** with warn ID **{warnid}**")
            
            await self.hc.db.execute("DELETE FROM warns WHERE guild=? AND user=? AND id=?", (interaction.guild.id, member.id, int(warnid)))
        elif warnid.lower() == "all":
            await self.hc.db.execute("DELETE FROM warns WHERE guild=? AND user=?", (interaction.guild.id, member.id))
            embed = helper.styling.SuccessEmbed(f"Deleted {member.display_name}'s warns", f"Deleted all warns for **{member.display_name}**")
        else:
            raise helper.errors.MildErr("Invalid Warn ID. Should be a number or 'all'")

        await interaction.response.send_message(embed=embed)

        # Log update if available
        embed = discord.Embed(title="Warn(s) deleted", color=var.embedFail, timestamp=datetime.now())
        embed.add_field(name="User:", value=str(member), inline=False)
        embed.add_field(name="Moderator", value=str(interaction.user))
        embed.add_field(name="ID", value=warnid)
        embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

        await functions.log(self.hc, "warns", interaction.guild, embed)
    
    @delwarn.autocomplete("warnid")
    async def _delwarn_warnid_autocomplete(self, interaction : discord.Interaction, namespace : str):
        values = interaction.namespace.__dict__
        return_list = []

        if values.get("member"):
            warns_raw = await self.hc.db.fetchall("SELECT id FROM warns WHERE guild=? AND user=?", (interaction.guild.id, values["member"].id))
            if len(warns_raw) > 1:
                return_list.append("all")
            for w in warns_raw:
                return_list.append(str(w[0]))
            
        
        return [app_commands.Choice(name=c, value=c) for c in return_list]

async def setup(bot):
    await bot.add_cog(Warns(bot, bot.hc))