from discord.ext import commands
from functions import customerror, functions
from setup import var

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
                        except:
                            pass
                    for guildRole in member.guild.roles:
                        if guildRole.name == "Muted":
                            await member.add_roles(guildRole)
        data = await functions.read_data("databases/joinleave.json")
        if str(member.guild.id) in data:
            if "join" in data[str(member.guild.id)]:
                try:
                    await self.bot.get_channel(int(data[str(member.guild.id)]["join"]["channel"])).send(functions.replaceMessage(member,data[str(member.guild.id)]["join"]["message"]))
                except:
                    pass
            if "autorole" in data[str(member.guild.id)]:
                try:
                    await member.add_roles(member.guild.get_role(int(data[str(member.guild.id)]["autorole"])))
                except Exception as e:
                    print(e)   
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        data = await functions.read_data("databases/joinleave.json")
        if str(member.guild.id) in data:
            if "leave" in data[str(member.guild.id)]:
                try:
                    await self.bot.get_channel(int(data[str(member.guild.id)]["leave"]["channel"])).send(functions.replaceMessage(member,data[str(member.guild.id)]["leave"]["message"]))
                except Exception as e:
                    print(e)

def setup(bot):
    bot.add_cog(Handling(bot))