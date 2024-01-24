from discord.ext import commands
from functions import functions
from setup import var
import discord
import random
import aiohttp
import helper

class Handling(commands.Cog):
    def __init__(self, bot : discord.Client):
        self.bot = bot
        self.hc : helper.HelperClient = bot.hc
    
    @commands.Cog.listener()
    async def on_member_join(self, member : discord.Member):
        joinleave_raw = await self.hc.db.fetchone("SELECT join_channel, join_message, leave_channel, leave_message FROM guildconfig_joinleave WHERE guild=?", (member.guild.id,))
        if joinleave_raw:
            if joinleave_raw[0] and joinleave_raw[1]:
                try:
                    await member.guild.get_channel(joinleave_raw[0]).send(functions.replaceMessage(member, joinleave_raw[1]))
                except Exception as e:
                    pass
        autorole_raw = await self.hc.db.fetchone("SELECT role FROM guildconfig_autorole WHERE guild=?", (member.guild.id,))
        if autorole_raw and autorole_raw[0]:
            try:
                await member.add_roles(member.guild.get_role(autorole_raw[0]))
            except Exception as e:
                print(e)   
    
    @commands.Cog.listener()
    async def on_member_remove(self, member : discord.Member):
        joinleave_raw = await self.hc.db.fetchone("SELECT leave_channel, leave_message FROM guildconfig_joinleave WHERE guild=?", (member.guild.id,))
        if joinleave_raw:
            if joinleave_raw[0] and joinleave_raw[1]:
                try:
                    await member.guild.get_channel(joinleave_raw[0]).send(functions.replaceMessage(member, joinleave_raw[1]))
                except Exception as e:
                    pass
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild : discord.Guild):
        print(guild.name)

        suitable_channel : discord.TextChannel = None 

        for channel in guild.text_channels:

            if ("chat" in channel.name or "general" in channel.name or "commands" in channel.name or "lounge" in channel.name or "bot" in channel.name) and channel.permissions_for(guild.me).send_messages:
                suitable_channel = channel 
        
        if suitable_channel == None:
            suitable_channel = random.choice(guild.text_channels)
        
        embed = discord.Embed(title="Thanks for adding me!", description=f"""
Thanks for adding me to your server!

Set up the bot on the [web dashboard]({var.address}/dashboard)

See my commands with `/help`
""", color=var.embed)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(style=discord.ButtonStyle.url, label="Web Dashboard", url=f"{var.address}/dashboard/{guild.id}"))

        await suitable_channel.send(content=var.server, embed=embed, view=view)

        # Support server message

        server_channel = self.bot.get_channel(var.support_guild_add_remove_channel)

        em = discord.Embed(title="Im In A New Server!", description=f"Server Name: **{guild.name}**", color=var.embedSuccess)
        em.add_field(name="Members: ", value=len(guild.members))
        em.set_thumbnail(url=guild.icon.url if guild.icon else None)
        em.add_field(name="ID: ", value= str(guild.id))
        em.add_field(name="Servers: ", value=f"I am now in **{len(self.bot.guilds)}** servers!")
        await server_channel.send(embed=em)

        await self.bot.change_presence(activity=discord.Game(name=f"/help | {var.version} | {len(self.bot.guilds)} servers"))
        
        if var.production:
            payload = {"server_count"  : len(self.bot.guilds)}
            async with aiohttp.ClientSession() as aioclient:
                await aioclient.post("https://discordbots.org/api/bots/486180321444888586/stats", data=payload, headers={"Authorization" : var.dblToken})
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild : discord.Guild):

        server_channel = self.bot.get_channel(var.support_guild_add_remove_channel)

        em = discord.Embed(title="I Was Removed From A Server.", description=f"Server Name: **{guild.name}**", color=var.embedFail)
        em.set_thumbnail(url=guild.icon.url if guild.icon else None)
        em.add_field(name="ID: ", value= str(guild.id))
        em.add_field(name="Servers: ", value=f"I am now in **{len(self.bot.guilds)}** servers!")
        await server_channel.send(embed=em)

        await self.bot.change_presence(activity=discord.Game(name=f"/help | {var.version} | {len(self.bot.guilds)} servers"))
        
        if var.production:
            payload = {"server_count"  : len(self.bot.guilds)}
            async with aiohttp.ClientSession() as aioclient:
                await aioclient.post("https://discordbots.org/api/bots/486180321444888586/stats", data=payload, headers={"Authorization" : var.dblToken})

async def setup(bot):
    await bot.add_cog(Handling(bot))