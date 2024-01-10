import quart
import os, json
from setup import var
from webserver.oauth import Oauth as oauth
from functions import functions, encryption
from functions import functions, customCommands
import discord 
import datetime
import resources
import helper

from discord.ext import commands

from discord import app_commands

loggingOptions = ["channelCreate", "channelDelete", "roleCreate", "roleDelete", "nicknameChange", "dashboardUse", "warns"]


def generate_app(bot : commands.Bot, hc : helper.HelperClient):

    app = quart.Quart(__name__, template_folder=os.path.abspath('./webserver/HTML'), static_folder=os.path.abspath('./webserver/static'))

    if not var.production:
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
        app.config["TEMPLATES_AUTO_RELOAD"] = True

    @app.route('/')
    async def home():
        return await quart.render_template('index.html', last_updated=dir_last_updated('/static'))

    @app.route('/about')
    async def about():
        return await quart.render_template('about.html', last_updated=dir_last_updated('/static'))

    @app.route('/changelogs')
    async def changelogs():
        return await quart.render_template('changelogs.html', last_updated=dir_last_updated('/static'))

    @app.route('/terms')
    async def terms():
        return await quart.render_template('terms_and_privacy.html', last_updated=dir_last_updated('/static'))

    @app.route('/invite')
    async def invite():
        return quart.redirect(var.invite)

    @app.route('/support')
    async def support():
        return quart.redirect(var.server)

    @app.route('/invited')
    async def invited():
        if quart.request.args.get("guild_id") == None:
            return quart.redirect("/")
        guildName = bot.get_guild(int(quart.request.args['guild_id'])) if bot.get_guild(int(quart.request.args['guild_id'])) else "None"
        return await quart.render_template('invited.html', last_updated=dir_last_updated('/static'), guild_name=guildName)

    @app.route('/api/changelogs', methods=['GET'])
    async def changelogsAPI():
        changelogs = {}
        for file in [f for f in os.listdir("./resources/changelogs/") if os.path.isfile(os.path.join("./resources/changelogs/", f))]:
            with open("resources/changelogs/" + file) as f:
                changelogs[file.replace(".html", "")] = f.read()

        return quart.jsonify(changelogs)

    @app.route('/api/commands', methods=['GET'])
    async def commandsAPI():
        commands = []
        done = []

        tree : app_commands.CommandTree = bot.tree

        commandsList = tree.walk_commands()

        cmdIter : list[app_commands.Command] = []
        for command in commandsList:
            if type(command) == app_commands.Group:
                for command1 in command.commands:
                    if type(command1) == app_commands.Group:
                        for command2 in command1.commands:
                            cmdIter.append(command2)
                    else:
                        cmdIter.append(command1)
            else:
                cmdIter.append(command)
        
        for command in cmdIter:
            
            if command.qualified_name not in done:
                done.append(command.qualified_name)
                category = None 
                for categoryIter in resources.commands.json:
                    if command.name in resources.commands.json[categoryIter]:
                        category = categoryIter

                options = [{"name":name, "description":str(option.description), "required":option.required} for name, option in command._params.items()]

                commands.append({"name":command.qualified_name, "description":str(command.description), "options":options, "category":category})
        
        return quart.jsonify(commands)

    @app.route('/api/userinfo', methods=['GET'])
    async def userinfoAPI():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
            name = encryption.decode(user[2], var.encryption_key)
            avatar = encryption.decode(user[3], var.encryption_key)
            user = bot.get_user(int(user_id))
        except AttributeError:
            return quart.jsonify({"user":None, "type":"unknown"})
        
        if not user:
            return quart.jsonify({
                "user":{
                    "id":user_id,
                    "name":name,
                    "avatar":avatar
                }, 
                "type":"user"
            })

        return quart.jsonify({
            "user":{
                "id":str(user.id),
                "name":user.name,
                "avatar":user.avatar.url if user.avatar else None,
                "mutual":[{"id":str(guild.id), "name":guild.name, "icon":guild.icon.url if guild.icon else None} for guild in bot.guilds if guild.get_member(int(user.id))]
            }, 
            "type":"mutual"
        })



    @app.route("/login", methods=["GET"])  
    async def admin():
        try:
            code = quart.request.args['code']
            access_token=oauth.get_access_token(code)
            user_json = oauth.get_user_json(access_token)
        except Exception as e:
            print(e)
            return quart.redirect(var.login)
        try:
            user_id = user_json["id"]
            user = bot.get_user(int(user_id))
            resp = await quart.make_response(quart.redirect("/#dashboard"))
            cookiestring = ''
            cookiestring = cookiestring + ';;;;' + encryption.encode(str(user_json['id']), var.encryption_key).decode("utf-8")
            cookiestring = cookiestring + ';;;;' + encryption.encode(str(user_json['username']), var.encryption_key).decode("utf-8")
            cookiestring = cookiestring + ';;;;' + encryption.encode(str(user_json['avatar']), var.encryption_key).decode("utf-8")
            resp.set_cookie('user', cookiestring, max_age=8_760*3600)
            return resp
        except AttributeError as e:
            print(e)
            return quart.redirect("/")

    @app.route('/dashboard')
    async def dashboard():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            resp = await quart.make_response(quart.redirect("/login"))
            resp.set_cookie('user', '', expires=0)
            return resp
        return await quart.render_template('dashboard.html', last_updated=dir_last_updated('/static'))

    @app.route('/dashboard/<server>')
    async def dashboardWith(server):
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")
        return await quart.render_template('dashboard.html', last_updated=dir_last_updated('/static'))

    async def jsonifyB(data, status=200, indent=4, sort_keys=True):
        response = await quart.make_response(json.dumps(dict(data), indent=indent, sort_keys=sort_keys))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['mimetype'] = 'application/json'
        response.status_code = status
        return response


    @app.route('/api/dashboard/serverDatabase')
    async def serverDataAPI():
        args = quart.request.args
        value = {}
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")
        warns = functions.read_data_sync('databases/warns.json')
        warnsString = json.dumps(warns)
        events = functions.read_data_sync("databases/events.json")
        
        with open("databases/commands.json") as f:
            commands = json.load(f)
        
        with open("databases/setup.json") as f:
            joinleaveData = json.load(f)

        if "guild" in args:
            if bot.get_guild(int(args["guild"])) != None:
                guild = bot.get_guild(int(args["guild"]))
                member = guild.get_member(int(user_id))
                bot_member = guild.get_member(bot.user.id)
                value[str(guild.id)] = {
                    "name":guild.name,
                    "id":str(guild.id),
                    "icon":guild.icon.key if guild.icon else "undefined",
                    "has_permissions":{"manage_messages":member.guild_permissions.manage_messages, "manage_guild":member.guild_permissions.manage_guild},
                    "joinleave":joinleaveData[str(guild.id)] if str(guild.id) in joinleaveData else {},
                    "warns":warns[str(guild.id)] if str(guild.id) in warns else {},
                    "owner":str(guild.owner_id),
                    "roles":[{"name":role.name,"id":str(role.id),"color":str(role.color)} for role in guild.roles],
                    "events":events[str(guild.id)] if str(guild.id) in events else [],
                    "members":[{"id":str(member.id),"tag":str(member)} for member in guild.members if str(member.id) in warnsString] if str(guild.id) in warns else {},
                    "text_channels":[{"name":channel.name,"id":str(channel.id), "permissions":{"send_messages":True if channel.permissions_for(bot_member).send_messages else False}} for channel in guild.text_channels],
                    "commands":commands[str(guild.id)] if str(guild.id) in commands else {},
                    "logging":joinleaveData[str(guild.id)]["logging"] if str(guild.id) in joinleaveData and "logging" in joinleaveData[str(guild.id)] else {}
                }
        else:
            for guild in bot.guilds:
                member = guild.get_member(int(user_id))
                bot_member = guild.get_member(bot.user.id)
                if member != None:
                    value[str(guild.id)] = {
                        "name":guild.name,
                        "id":str(guild.id),
                        "icon":guild.icon.key if guild.icon else "undefined"
                        
                    }
        if "b" in args:
            return await jsonifyB(value)
        return quart.jsonify(value)

    @app.route('/api/dashboard/setAutorole', methods=['POST'])
    async def setAutorole():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")

        with open("databases/setup.json") as f:
            joinleave = json.load(f)

        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))

        try:
            role = data["role"]
        except AttributeError:
            return quart.jsonify({"error":"Invalid role"})
        
        if member.guild_permissions.manage_guild:
            if str(guild.id) not in joinleave:
                joinleave[str(guild.id)] = {}
            if role == "None" and "autorole" in joinleave[str(guild.id)]:
                what = "removed"
                del joinleave[str(guild.id)]["autorole"]
            elif role == "None":
                what = "removed"
            else:
                what = "set"
                joinleave[str(guild.id)]["autorole"] = str(role)
            functions.save_data_sync("databases/setup.json", joinleave)
            functions.read_load_sync("databases/setup.json", joinleave)

            # Log update if available
            embed = discord.Embed(title="Autorole role updated", color=var.embed, timestamp=datetime.datetime.now())
            embed.add_field(name="New:", value=guild.get_role(int(role)).mention, inline=False)
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

            bot.loop.create_task(functions.log(bot, "dashboardUse", guild, embed))
                
            return quart.jsonify({"data":joinleave[str(guild.id)], "returnMessage":f"Successfully {what} autorole role"})

        return quart.jsonify({"error":"Missing perms"})

    @app.route('/api/dashboard/setLogging', methods=['POST'])
    async def setLogging():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")

        with open("databases/setup.json") as f:
            joinleave = json.load(f)

        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))

        try:
            loggingData = data["logging"]
        except AttributeError:
            return quart.jsonify({"error":"Invalid role"})
        
        if "channel" in loggingData:
            if loggingData["channel"] == "0":
                del loggingData["channel"]
        
        if member.guild_permissions.manage_guild:
            if str(guild.id) not in joinleave:
                joinleave[str(guild.id)] = {}

            joinleave[str(guild.id)]["logging"] = loggingData

            loggingSettings = "_ _ "
            
            for option in loggingOptions:
                if option in loggingData["ignore"]:
                    loggingSettings += f"{option}: **F**alse\n"
                else:
                    loggingSettings += f"{option}: **T**rue\n"

            # Log update if available
            embed = discord.Embed(title="Logging setting updated", color=var.embed, timestamp=datetime.datetime.now())
            embed.add_field(name="Channel:", value=f"<#{loggingData['channel'] if 'channel' in loggingData else 'None'}>", inline=False)
            embed.add_field(name="Settings:", value=loggingSettings, inline=False)
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

            bot.loop.create_task(functions.log(bot, "dashboardUse", guild, embed))

            functions.save_data_sync("databases/setup.json", joinleave)
            functions.read_load_sync("databases/setup.json", joinleave)
                
            return quart.jsonify({"data":joinleave[str(guild.id)], "returnMessage":f"Successfully set logging settings"})

        return quart.jsonify({"error":"Missing perms"})

    @app.route('/api/dashboard/setMessage', methods=['POST'])
    async def setMessage():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")
        
        with open("databases/setup.json") as f:
            joinleave = json.load(f)

        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))

        try:
            channel = int(data["channel"])
            message = data["message"]
            choice = data["type"]
        except AttributeError:
            return quart.jsonify({"error":"Invalid channel/message"})
        
        if member.guild_permissions.manage_guild:
            if message.replace(" ", "") == "" and str(guild.id) in joinleave and choice in joinleave[str(guild.id)]:
                del joinleave[str(guild.id)][choice]
            elif message.replace(" ", "") == "" and (str(guild.id) not in joinleave or choice not in joinleave[str(guild.id)]):
                pass
            elif len(message) > 1900:
                return quart.jsonify({"error":"Message over 1900 characters"})
            else:
                if str(guild.id) not in joinleave:
                    joinleave[str(guild.id)] = {}
                if choice not in joinleave[str(guild.id)]:
                    joinleave[str(guild.id)][choice] = {}
                joinleave[str(guild.id)][choice] = {"channel":str(channel),"message":message}

            functions.save_data_sync("databases/setup.json", joinleave)
            functions.read_load_sync("databases/setup.json", joinleave)

            # Log update if available
            embed = discord.Embed(title=f"{choice.title()} message updated", color=var.embed, timestamp=datetime.datetime.now())
            embed.add_field(name="Type:", value=choice.title(), inline=False)
            embed.add_field(name="Channel:", value=f"<#{channel}>", inline=False)
            embed.add_field(name="Message:", value=message, inline=False)
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url)

            bot.loop.create_task(functions.log(bot, "dashboardUse", guild, embed))

            return quart.jsonify({"data":joinleave[str(guild.id)], "returnMessage":f"Successfully set {choice} message to '{data['message']}'"})

        return quart.jsonify({"error":"Missing perms"})

    @app.route('/api/dashboard/setEvents', methods=['POST'])
    async def setEvents():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")
        events = functions.read_data_sync("databases/events.json")
        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))
        if member.guild_permissions.manage_guild:
            if len(data["events"]) > 10:
                return quart.jsonify({"error":"You have hit the maximum amount of events for the server (10)!"})
            events[str(guild.id)] = data["events"]
            functions.save_data_sync("databases/events.json", events)

            eventsText = "_ _ "
            counter = 0
            for event in data["events"]:
                counter += 1
                eventsText += f"{counter}. At **{event['amount']} {event['what']}**, **{event['action']}**.\n"

            # Log update if available
            embed = discord.Embed(title="Events updated", color=var.embed, timestamp=datetime.datetime.now())
            embed.add_field(name="Events:", value=eventsText, inline=False)
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

            bot.loop.create_task(functions.log(bot, "dashboardUse", guild, embed))

            return quart.jsonify({"returnMessage":"Successfully set events"})
        
        return quart.jsonify({"error":"Missing perms"})

    @app.route('/api/dashboard/setCustomCommands', methods=['POST'])
    async def setCustomCommands():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")

        commands = functions.read_data_sync("databases/commands.json")

        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))

        if member.guild_permissions.manage_guild:
            if len(data["commands"]) > 10:
                return quart.jsonify({"error":"You have hit the maximum amount of custom commands for the server (10)!"})
            
            did = False
            did2 = False
            delList = []

            for cmd in data["commands"]:
                # SlashCommand
                for command in bot.commands:
                    if cmd == command.name and command.guild_ids == [guild.id] and "Custom Command" in command.description:
                        pass
                    elif cmd == command.name:
                        delList.append(cmd)
                        did = True
                
                if cmd.replace(" ", "") == "" or data["commands"][cmd].replace(" ", "") == "":
                    delList.append(cmd)
                    did2 = True
            
            for item in delList:
                del data["commands"][item]
            
            

            commands[str(guild.id)] = data["commands"]

            functions.save_data_sync("databases/commands.json", commands)
            functions.read_load_sync("databases/commands.json", commands)

            
            bot.loop.create_task(customCommands.sync_custom_commands(bot, guild=guild))

            # Log update if available
            embed = discord.Embed(title="Custom Commands updated", color=var.embed, timestamp=datetime.datetime.now())
            embed.add_field(name="Commands:", value=f"Too many to send here. View them on the [Web Dashboard]({var.address}#dashboard)", inline=False)
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

            bot.loop.create_task(functions.log(bot, "dashboardUse", guild, embed))
            

            if did == True:
                return quart.jsonify({"error":"One or more of your custom commands already exist! Removed them.", "commands":commands[str(guild.id)]})
            if did2 == True:
                return quart.jsonify({"error":"One or more of your custom commands were empty! Removed them.", "commands":commands[str(guild.id)]})

            return quart.jsonify({"returnMessage":"Successfully set commands. This may take up to a minute to refresh.", "commands":commands[str(guild.id)]})

        
        return quart.jsonify({"error":"Missing perms", "commands":commands[str(guild.id)]})

    @app.route('/api/dashboard/delWarn', methods=['POST'])
    async def delWarn():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")
        warns = functions.read_data_sync("databases/warns.json")
        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))
        if member.guild_permissions.manage_messages:
            del warns[str(guild.id)][data['member']][data['id']]
            functions.save_data_sync("databases/warns.json", warns)
            warns["returnMessage"] = f"Successfully deleted warn {data['id']}"

            # Log update if available
            embed = discord.Embed(title="Warn deleted (from dashboard)", color=var.embedFail, timestamp=datetime.datetime.now())
            embed.add_field(name="User:", value=f"<@{data['member']}>", inline=False)
            embed.add_field(name="Moderator", value=str(member))
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

            bot.loop.create_task(functions.log(bot, "warns", guild, embed))

            return quart.jsonify(warns)

        return quart.jsonify({"error":"Missing perms"})


    def dir_last_updated(folder):
        try:
            return str(max(os.path.getmtime(os.path.join(root_path, f)) for root_path, dirs, files in os.walk(folder) for f in files))
        except ValueError:
            pass

    return app
