import discord, random, os, json, re
from discord.ext import commands
from functions import customerror, functions
from setup import var
from EasyConversion import textformat

class Handling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        

        
        msgMild = random.choice(["Uh oh!", "Oops!", "Oh no!"])
        msgUnkown = random.choice(["You've ran into an unknown error!", "You've ran into an error!"])
        if isinstance(error, commands.MemberNotFound):
            embed = discord.Embed(title=msgMild, description=f"```{str(error)}```", colour=var.embedFail, timestamp=ctx.message.created_at)
            return await ctx.send(embed=embed)
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title=msgMild, description=f"```{error}\n{functions.prefix(ctx.guild)}{ctx.command.name} {ctx.command.description.split('|')[0]}```", colour=var.embedFail, timestamp=ctx.message.created_at)
            return await ctx.send(embed=embed)
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title=msgMild, description=f"```{error}```", colour=var.embedFail, timestamp=ctx.message.created_at)
            return await ctx.send(embed=embed)
        if isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(title=msgMild, description=f"```{error}\n\nEnsure that I have the above permissions and my role is high enough to use {ctx.command.name}```", colour=var.embedFail, timestamp=ctx.message.created_at)
            return await ctx.send(embed=embed)
        if isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(title=msgMild, description=f"```{error}```", colour=var.embedFail, timestamp=ctx.message.created_at)
            return await ctx.send(embed=embed)
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(title=msgMild, description=f"{error}", colour=var.embedFail)
            return await ctx.send(embed=embed)
        if isinstance(error, commands.CommandNotFound):
            cc = await self.customCommands(ctx, error)
            if cc == False:
                return await self.bot.get_user(var.owner).send(f"> Error in **{ctx.guild.name}** from **{ctx.author}**: `{error}`")
            else:
                return
            
        
        if isinstance(error, commands.CommandInvokeError):
            if isinstance(error.original, customerror.CustomErr):
                embed = discord.Embed(title=msgMild, description=f"```{error.original}```", colour=var.embedFail, timestamp=ctx.message.created_at)
                return await ctx.send(embed=embed)
            if isinstance(error.original, customerror.MildErr):
                embed = discord.Embed(title=msgMild, description=f"{error.original}", colour=var.embedFail)
                return await ctx.send(embed=embed)

        print(f"{textformat.color.red}{error.__class__.__name__}{textformat.color.end} + {error}")
        embed = discord.Embed(title=msgUnkown, description=f"```{error}```\n\nJoin the [Support Server]({var.server}) for support.", colour=var.embedFail, timestamp=ctx.message.created_at)
        await ctx.send(embed=embed)
        await self.bot.get_user(var.owner).send(f"> Error in **{ctx.guild.name}** from **{ctx.author}**: `{error}`")
    
    async def customCommands(self, ctx, error):

        commands = str(error).replace('Command "', '')
        commands = commands.replace('" is not found', '')

        with open("databases/commands.json") as f:
            data = json.load(f)
        
        if commands in data[str(ctx.guild.id)]:
            resp = data[str(ctx.guild.id)][commands]

            brackets = re.findall(r"\{(.*?)\}",resp)
            
            for bracket in brackets:
                try:
                    split = bracket.split("/")
                    bracketType = split[0]
                    if bracketType.lower() in ["args", "arg", "arguments", "argument"]:
                        args = ctx.message.content.split(" ")

                        if split[1][-1] == ":":
                            split[1] = split[1].replace(":", "")
                            arg = args[int(split[1]):]
                            search = "%s" % (" ".join(arg))
                            if search.replace(" ", "") == "":
                                resp = resp.replace("{" + bracket + "}", "None")
                        else:
                            arg = args[int(split[1])]
                            search = "%s" % ("".join(arg))
                        
                        
                        resp = resp.replace("{" + bracket + "}", search)

                    if bracketType.lower() in ["randomchoice", "random-choice", "random"]:
                        
                        randomChoice = random.choice(split[1:])
                        
                        resp = resp.replace("{" + bracket + "}", randomChoice)

                except Exception as e:
                    print(e)
                    resp = resp.replace("{" + bracket + "}", "None")

            await ctx.send(resp, allowed_mentions=discord.AllowedMentions(everyone=False, roles=False))
        
            return True
        else:
            return False
        

def setup(bot):
    bot.add_cog(Handling(bot))