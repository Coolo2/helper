import discord, random, os, json
from discord.ext import commands
from setup import var
from functions import customerror
from functions import functions

class Setup1(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="prefix", description="*[prefix/reset]|Set or get prefix for a server", aliases=['getprefix', 'setprefix', 'get-prefix', 'set-prefix'])
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, prefix = None):
        currentPrefix = functions.prefix(ctx.guild)
        data = await functions.read_data("databases/prefixes.json")
        if prefix == None:
            return await ctx.send(
                    embed=discord.Embed(
                        title=random.choice([f"Here's the prefix for {ctx.guild.name}", "Here's the prefix", f"Here's my prefix for {ctx.guild.name}"]), 
                        description=f"The prefix for {ctx.guild.name} is **{currentPrefix}**",
                        colour=var.embed
                )
            )
        elif prefix == currentPrefix:
            raise customerror.MildErr(f"The prefix for **{ctx.guild.name}** is already set to **{prefix}**!")
        elif prefix in ['reset', var.prefix]:
            if str(ctx.guild.id) in data:
                del data[str(ctx.guild.id)]
                await ctx.send(
                    embed=discord.Embed(
                        title=random.choice([f"Resetted the prefix for {ctx.guild.name}", "Resetted your prefix!", "Complete!", "Successfully resetted!"]),
                        description=f"Successfully resetted the prefix for **{ctx.guild.name}** to **{var.prefix}**",
                        colour=var.embedSuccess
                    )
                )
            else:
                raise customerror.MildErr(f"The prefix for **{ctx.guild.name}** is already reset to **{var.prefix}**!")
        else:
            data[str(ctx.guild.id)] = prefix
            await ctx.send(
                embed=discord.Embed(
                    title=random.choice([f"Set the prefix for {ctx.guild.name}", "Set your prefix!", "Complete!", "Successfully set!"]),
                    description=f"Successfully set the prefix for **{ctx.guild.name}** to **{prefix}**",
                    colour=var.embedSuccess
                )
            )
        await functions.save_data("databases/prefixes.json", data)

        await functions.read_load("databases/prefixes.json", data)
    
    @commands.command(name="setup")
    async def setup(self, ctx):
        return await ctx.send(embed=discord.Embed(
            title="Setup has moved!",
            description=f"Setup has moved to the [web dashboard]({var.website}/dashboard#{ctx.guild.id})!",
            colour=var.embed
        ))
    
    @commands.command(name="customcommands", description="View all custom commands for the server", aliases=['ccs'])
    async def customcommands(self, ctx):
        embed = discord.Embed(title=f"Custom commands for {ctx.guild.name}", color=var.embed)
        
        with open("databases/commands.json") as f:
            customCommands = json.load(f)

        if str(ctx.guild.id) not in customCommands:
            return await ctx.send(f"This server does not have any custom commands! Add some on the web dashboard (`{functions.prefix(ctx.guild)}dashboard`)!")

        for command in customCommands[str(ctx.guild.id)]:
            value = customCommands[str(ctx.guild.id)][command][0:60] + ("..." if len(customCommands[str(ctx.guild.id)][command][0:60]) <= 60 else "")

            embed.add_field(name=command, value=value, inline=False)
        
        embed.add_field(name="More", value=f"View more and edit custom commands on the [Web Dashboard]({var.address}/dashboard)", inline=False)

        await ctx.send(embed=embed)
            
        

def setup(bot):
    bot.add_cog(Setup1(bot))