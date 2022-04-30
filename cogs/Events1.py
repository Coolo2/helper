from discord.ext import commands
from functions import functions
from setup import var
import discord
import random
import aiohttp

class Handling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        data = await functions.read_data("databases/mutes.json")
        
        for guild in data:
            for memberJ in data[guild]:
                if memberJ == str(member.id):
                    for memberRole in member.roles:
                        try:
                            await member.remove_roles(memberRole)
                        except Exception as e:
                            pass
                    for guildRole in member.guild.roles:
                        if guildRole.name == "Muted":
                            await member.add_roles(guildRole)
        data = await functions.read_data("databases/setup.json")
        if str(member.guild.id) in data:
            if "join" in data[str(member.guild.id)]:
                try:
                    await self.bot.get_channel(int(data[str(member.guild.id)]["join"]["channel"])).send(functions.replaceMessage(member,data[str(member.guild.id)]["join"]["message"]))
                except Exception as e:
                    pass
            if "autorole" in data[str(member.guild.id)]:
                try:
                    await member.add_roles(member.guild.get_role(int(data[str(member.guild.id)]["autorole"])))
                except Exception as e:
                    print(e)   
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = await functions.read_data("databases/setup.json")
        if str(member.guild.id) in data:
            if "leave" in data[str(member.guild.id)]:
                try:
                    await self.bot.get_channel(int(data[str(member.guild.id)]["leave"]["channel"])).send(functions.replaceMessage(member,data[str(member.guild.id)]["leave"]["message"]))
                except Exception as e:
                    print(e)
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild : discord.Guild):

        # Channel message

        print(guild.name)

        suitable_channel : discord.TextChannel = None 

        for channel in guild.text_channels:

            if ("chat" in channel.name or "general" in channel.name or "commands" in channel.name or "lounge" in channel.name or "bot" in channel.name) and channel.can_send():
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
        em.set_thumbnail(url=guild.icon.url)
        em.add_field(name="ID: ", value= str(guild.id))
        em.add_field(name="Servers: ", value=f"I am now in **{len(self.bot.guilds)}** servers!")
        await server_channel.send(embed=em)

        await self.bot.change_presence(activity=discord.Game(name=f"/help | b{var.version} | {len(self.bot.guilds)} servers"))
        
        if var.production:
            payload = {"server_count"  : len(self.bot.guilds)}
            async with aiohttp.ClientSession() as aioclient:
                await aioclient.post("https://discordbots.org/api/bots/486180321444888586/stats", data=payload, headers={"Authorization" : var.dblToken})
    
    @commands.Cog.listener()
    async def on_guild_remove(self, guild : discord.Guild):

        server_channel = self.bot.get_channel(var.support_guild_add_remove_channel)

        em = discord.Embed(title="I Was Removed From A Server.", description=f"Server Name: **{guild.name}**", color=var.embedFail)
        em.set_thumbnail(url=guild.icon.url)
        em.add_field(name="ID: ", value= str(guild.id))
        em.add_field(name="Servers: ", value=f"I am now in **{len(self.bot.guilds)}** servers!")
        await server_channel.send(embed=em)

        await self.bot.change_presence(activity=discord.Game(name=f"/help | b{var.version} | {len(self.bot.guilds)} servers"))
        
        if var.production:
            payload = {"server_count"  : len(self.bot.guilds)}
            async with aiohttp.ClientSession() as aioclient:
                await aioclient.post("https://discordbots.org/api/bots/486180321444888586/stats", data=payload, headers={"Authorization" : var.dblToken})

async def setup(bot):
    await bot.add_cog(Handling(bot))