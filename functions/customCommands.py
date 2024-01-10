
import discord, json, re, random

from discord.ext import commands

from discord import app_commands

from setup import var

n = None

def testFunc(cmdGuild, cmdName, cmdValue):

    async def testFuncInside(ctx : discord.Interaction, arg1 : str =n, arg2 : str =n, arg3 : str =n, arg4 : str =n, arg5 : str =n, arg6 : str =n, arg7 : str =n, arg8 : str =n, arg9 : str =n, arg10 : str =n):
        with open("databases/commands.json") as f:
            data = json.load(f)
        
        if str(ctx.guild.id) not in data:
            return 
        if cmdName not in data[str(ctx.guild.id)]:
            return await ctx.response.send_message("`Command no longer exists and will be removed on next sync`")
        
        resp = data[str(ctx.guild.id)][cmdName] 

        args = ["", arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10]
        args = [x for x in args if x is not None]

        brackets = re.findall(r"\{(.*?)\}",resp)
        
            
        for bracket in brackets:

            split = bracket.split("/")
            bracketType = split[0]

            if bracketType.lower() in ["args", "arg", "arguments", "argument"]:
                arg = args[int(split[1])]
                search = arg
                resp = resp.replace("{" + bracket + "}", search)  
            if bracketType.lower() in ["randomchoice", "random-choice", "random"]:              
                randomChoice = random.choice(split[1:])     
                resp = resp.replace("{" + bracket + "}", randomChoice)     
            if bracketType.lower() in ["member", "user", "membername", "username", "member-name", "user-name"]:
                resp = resp.replace("{" + bracket + "}", ctx.user.name)
            if bracketType.lower() in ["nickname", "nick-name"]:
                resp = resp.replace("{" + bracket + "}", ctx.user.display_name)
            if bracketType.lower() in ["@member", "@user", "@member-name", "@username"]:
                resp = resp.replace("{" + bracket + "}", ctx.user.mention)
            if bracketType.lower() in ["server", "guild", "servername", "guildname", "server-name", "guild-name"]:
                resp = resp.replace("{" + bracket + "}", ctx.guild.name)

        return await ctx.response.send_message(resp)
    
    return testFuncInside

class CustomCommand():
    def __init__(self, name : str, value : str):
        self.name = name 
        self.value = value 
        self.rawOptions = []
        
        self.options = self.generate_options()
        
    
    def generate_options(self):

        options = []
        rawOptions = []

        counter = 0
        for i in range(10):
            for argAlias in ["args", "arg", "arguments", "argument"]:
                if f"{argAlias}/{i}" in self.value:
                    
                    counter += 1
                    opt = {"type":str, "name":f"arg{counter}", "required":True}

                    #opt.__setattr__("_parameter_name", f"arg{counter}")
                    options.append(opt)
                    rawOptions.append(f"arg{counter}")

        self.options = options
        self.rawOptions = rawOptions

        return self.options


async def sync_custom_commands(bot : commands.Bot, guild : discord.Guild = None):
    tree : app_commands.CommandTree = bot.tree

    print("Custom commands syncing...")

    with open("databases/commands.json") as f:
        data = json.load(f)

    for guild_id in data:
        if guild and str(guild_id) != str(guild.id):
            continue
        await doGuildCustomCommands(bot, int(guild_id), data[guild_id])

    cmds = tree._guild_commands

    

    for guild_id, guild_cmds in cmds.items():
        to_remove = []

        if guild and str(guild_id) != str(guild.id):
            continue

        for name, cmd in guild_cmds.items():

            if cmd.description and "Helper Bot Custom Command" in cmd.description:

                if str(guild_id) not in data or name not in data[str(guild_id)]:
                    to_remove.append([name, discord.Object(guild_id)])
        
        for command in to_remove:
            tree.remove_command(command[0], guild=command[1])
                    
        if var.reload_custom_commands:
            if bot.get_guild(guild_id):
                await tree.sync(guild=discord.Object(guild_id))
                print("synced")
            else:
                print("missing guild")
        else:
            print("Warning: custom command reloading is disabled!")
    
    

async def doGuildCustomCommands(bot : commands.Bot, guild_id : int, pendingCommands : dict):
    tree : app_commands.CommandTree = bot.tree

    for pendingCommand in pendingCommands:
        command = CustomCommand(pendingCommand, pendingCommands[pendingCommand])

        func = testFunc(guild_id, command.name, command.value)

        for option in command.options:
            print(option)

        cmd = app_commands.Command(
            callback=func, 
            name=command.name, 
            description=f"Helper Bot Custom Command: {command.name}"
        )

        for i, (name, param) in enumerate(cmd._params.items()):
            if len(command.options) > i:

                cmd._params[name].required = True
        

        try:
            tree.add_command(cmd, guild=discord.Object(guild_id), override=True)
            
        except app_commands.errors.CommandAlreadyRegistered:
            tree.remove_command(cmd, guild=discord.Object(guild_id))       
            tree.add_command(cmd, guild=discord.Object(guild_id))
        

