import discord, json, re, random

n = None

def testFunc(cmdGuild, cmdName, cmdValue):

    async def testFuncInside(ctx, arg1=n, arg2=n, arg3=n, arg4=n, arg5=n, arg6=n, arg7=n, arg8=n, arg9=n, arg10=n):
        with open("databases/commands.json") as f:
            data = json.load(f)
        
        if str(ctx.guild.id) not in data:
            return 
        
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

        return await ctx.respond(resp)
    
    return testFuncInside

def loadCustomCommands(bot : discord.Bot, returnList=False):
    
    with open("databases/commands.json") as f:
        data = json.load(f)
    final = []
    
    for guildID in data:
        for commandName in data[guildID]:
            options = []

            commandValue = data[guildID][commandName]

            counter = 0
            for i in range(10):
                for argAlias in ["args", "arg", "arguments", "argument"]:
                    if f"{argAlias}/{i}" in commandValue:
                        
                        counter += 1
                        opt = discord.Option(str, name=f"arg{counter}", required=True)
                        opt.__setattr__("_parameter_name", f"arg{counter}")
                        options.append(opt)
                        commandValue = commandValue.replace(f"{argAlias}/{i}", f"args/{counter}")
            
            func = testFunc(int(guildID), commandName, commandValue)

            cmd = discord.SlashCommand(
                func=func, 
                callback=func, 
                name=commandName, 
                description=f"Helper Bot Custom Command: {commandName}", 
                options=options,
                guild_ids=[int(guildID)]
            )
            if returnList:
                final.append(cmd.to_dict())
                continue

            bot.add_application_command(cmd)
    
    return final