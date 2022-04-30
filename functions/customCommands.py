from turtle import update
import discord, json, re, random

from discord.ext import commands

n = None

def testFunc(cmdGuild, cmdName, cmdValue):

    async def testFuncInside(ctx, arg1=n, arg2=n, arg3=n, arg4=n, arg5=n, arg6=n, arg7=n, arg8=n, arg9=n, arg10=n):
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
                resp = resp.replace("{" + bracket + "}", ctx.author.name)
            if bracketType.lower() in ["nickname", "nick-name"]:
                resp = resp.replace("{" + bracket + "}", ctx.author.display_name)
            if bracketType.lower() in ["@member", "@user", "@member-name", "@username"]:
                resp = resp.replace("{" + bracket + "}", ctx.author.mention)
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
                    opt = discord.Option(str, name=f"arg{counter}", required=True)
                    opt.__setattr__("_parameter_name", f"arg{counter}")
                    options.append(opt)
                    rawOptions.append(f"arg{counter}")
        self.options = options
        self.rawOptions = rawOptions
        return self.options


async def sync_custom_commands(bot : commands.Bot):

    print("Custom commands syncing...")
    unregister_guilds = []

    with open("databases/commands.json") as f:
        data = json.load(f)
    
    toRemove = []
    update_commands = []

    for guild_id in data:
        if not bot.get_guild(int(guild_id)):
            toRemove.append(guild_id)
    
    for removeable in toRemove:
        del data[removeable]
    
    for guild_id in data:
        await doGuildCustomCommands(bot, int(guild_id), data[guild_id])

    for command in bot.commands:
        if command.guild_ids and len(command.guild_ids) > 0 and (str(command.guild_ids[0]) in data and command.name not in data[str(command.guild_ids[0])]) and "Helper Bot Custom Command" in command.description:
            unregister_guilds.append(command.guild_ids[0])
            bot.remove_application_command(command)

    

    for command in bot.pending_application_commands:
        if 'Helper Bot Custom Command' in command.description:
            update_commands.append(command)

    #await bot.sync_commands(unregister_guilds=unregister_guilds)

    #print("Custom commands synced...")

async def doGuildCustomCommands(bot : commands.Bot, guild_id : int, pendingCommands : dict):

    #bot._pending_application_commands = []

    for pendingCommand in pendingCommands:
        command = CustomCommand(pendingCommand, pendingCommands[pendingCommand])

        func = testFunc(guild_id, command.name, command.value)

        cmd = discord.SlashCommand(
            func=func, 
            callback=func, 
            name=command.name, 
            description=f"Helper Bot Custom Command: {command.name}", 
            options=command.options,
            guild_ids=[guild_id]
        )

        

        bot.add_application_command(cmd)
        

