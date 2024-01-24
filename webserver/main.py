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
        
        for command in hc.commands_list:
            category_name = helper.utils.category_name_from_cog_name(command.module)
            options = [{"name":name, "description":str(option.description), "required":option.required} for name, option in command._params.items()]

            commands.append({"name":command.qualified_name, "description":str(command.description), "options":options, "category":category_name})
        
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

        if "guild" in args:
            if bot.get_guild(int(args["guild"])) != None:
                guild = bot.get_guild(int(args["guild"]))
                member = guild.get_member(int(user_id))
                bot_member = guild.get_member(bot.user.id)

                warns_raw = await hc.db.fetchall("SELECT id, CAST(user AS text), time, CAST(mod AS text), reason FROM warns WHERE guild=?", (guild.id,))
                commands_raw = await hc.db.fetchall("SELECT name, value FROM custom_commands WHERE guild=?", (guild.id,))
                joinleave_raw = await hc.db.fetchone("SELECT CAST(join_channel AS text), join_message, CAST(leave_channel AS text), leave_message FROM guildconfig_joinleave WHERE guild=?", (guild.id,))
                logging_raw = await hc.db.fetchone("SELECT CAST(channel AS text), ignore FROM guildconfig_logging WHERE guild=?", (guild.id,))
                autorole_raw = await hc.db.fetchone("SELECT CAST(role AS text) FROM guildconfig_autorole WHERE guild=?", (guild.id,))
                events_raw = await hc.db.fetchall("SELECT amount, what, action FROM events WHERE guild=?", (guild.id,))
                
                if logging_raw:
                    logging_raw = list(logging_raw)
                    if type(logging_raw[1]) == str and "," in logging_raw[1]:
                        logging_raw[1] = logging_raw[1].split(",")

                value[str(guild.id)] = {
                    "name":guild.name,
                    "id":str(guild.id),
                    "icon":guild.icon.key if guild.icon else "undefined",
                    "has_permissions":{"manage_messages":member.guild_permissions.manage_messages, "manage_guild":member.guild_permissions.manage_guild},
                    "joinleave":joinleave_raw,
                    "warns":warns_raw,
                    "owner":str(guild.owner_id),
                    "roles":[{"name":role.name,"id":str(role.id),"color":str(role.color)} for role in guild.roles],
                    "events":events_raw,
                    "members":[{"id":str(member.id),"tag":str(member)} for member in guild.members if member.id in [w[1] for w in warns_raw]+[w[3] for w in warns_raw]],
                    "text_channels":[{"name":channel.name,"id":str(channel.id), "permissions":{"send_messages":True if channel.permissions_for(bot_member).send_messages else False}} for channel in guild.text_channels],
                    "commands":commands_raw,
                    "logging":logging_raw,
                    "autorole":autorole_raw[0] if autorole_raw else None
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

        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))

        try:
            role = data["role"]
        except AttributeError:
            return quart.jsonify({"error":"Invalid role"})
        
        if member.guild_permissions.manage_guild:
            exists = await hc.db.fetchone("SELECT guild FROM guildconfig_autorole WHERE guild=?", (guild.id,))
            
            if role == "None":
                what = "removed"
                await hc.db.execute("DELETE FROM guildconfig_autorole WHERE guild=?", (guild.id,))
            else:
                what = "set"
                if exists:
                    await hc.db.execute("UPDATE guildconfig_autorole SET role=? WHERE guild=?", (int(role), guild.id))
                else:
                    await hc.db.execute("INSERT INTO guildconfig_autorole VALUES (?, ?)", (guild.id, int(role)))

            # Log update if available
            embed = discord.Embed(title="Autorole role updated", color=var.embed, timestamp=datetime.datetime.now())
            embed.add_field(name="New:", value=guild.get_role(int(role)).mention, inline=False)
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

            bot.loop.create_task(functions.log(hc, "dashboardUse", guild, embed))

            autorole_raw = await hc.db.fetchone("SELECT CAST(role AS text) FROM guildconfig_autorole WHERE guild=?", (guild.id,))
                
            return quart.jsonify({"data":autorole_raw[0] if autorole_raw else None, "returnMessage":f"Successfully {what} autorole role"})

        return quart.jsonify({"error":"Missing perms"})

    @app.route('/api/dashboard/setLogging', methods=['POST'])
    async def setLogging():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")

        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))

        exists = await hc.db.fetchone("SELECT guild FROM guildconfig_logging WHERE guild=?", (guild.id,))

        try:
            loggingData = data["logging"]
        except AttributeError:
            return quart.jsonify({"error":"Invalid role"})
        
        if loggingData.get("channel") == "0":
            del loggingData["channel"]
        
        print(loggingData)
        
        if member.guild_permissions.manage_guild:

            if exists:
                await hc.db.execute("UPDATE guildconfig_logging SET channel=?, ignore=?", (
                    int(loggingData.get("channel")) if loggingData.get("channel") else None, ",".join(loggingData.get("ignore")) if loggingData.get("ignore") else None))
            else:
                await hc.db.execute("INSERT INTO guildconfig_logging VALUES (?, ?, ?)", (guild.id, int(loggingData.get("channel")) if loggingData.get("channel") else None, ",".join(loggingData.get("ignore")) if loggingData.get("ignore") else None))

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

            bot.loop.create_task(functions.log(hc, "dashboardUse", guild, embed))

            logging_raw = await hc.db.fetchone("SELECT CAST(channel AS text), ignore FROM guildconfig_logging WHERE guild=?", (guild.id,))
            
                
            return quart.jsonify({"data":logging_raw, "returnMessage":f"Successfully set logging settings"})

        return quart.jsonify({"error":"Missing perms"})

    @app.route('/api/dashboard/setMessage', methods=['POST'])
    async def setMessage():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")
        
        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))

        try:
            channel = int(data["channel"])
            message = data["message"]
            choice = data["type"]

            if choice not in ["join", "leave"]: raise
        except AttributeError:
            return quart.jsonify({"error":"Invalid channel/message"})
        
        if member.guild_permissions.manage_guild:
            if (channel == 0 or message.replace(" ", "") == ""):
                await hc.db.execute(f"UPDATE guildconfig_joinleave SET {choice}_channel=?, {choice}_message=?", (None, None))
            elif len(message) > 1900:
                return quart.jsonify({"error":"Message over 1900 characters"})
            else:
                exists = await hc.db.fetchone("SELECT guild FROM guildconfig_joinleave WHERE guild=?", (guild.id,))

                if exists:
                    await hc.db.execute(f"UPDATE guildconfig_joinleave SET {choice}_channel=?, {choice}_message=?", (channel, message))
                else:
                    await hc.db.execute(f"INSERT INTO guildconfig_joinleave (guild, {choice}_channel, {choice}_message) VALUES (?, ?, ?)", (guild.id, channel, message))

            # Log update if available
            embed = discord.Embed(title=f"{choice.title()} message updated", color=var.embed, timestamp=datetime.datetime.now())
            embed.add_field(name="Type:", value=choice.title(), inline=False)
            embed.add_field(name="Channel:", value=f"<#{channel}>", inline=False)
            embed.add_field(name="Message:", value=message, inline=False)
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url)

            bot.loop.create_task(functions.log(hc, "dashboardUse", guild, embed))

            joinleave_raw = await hc.db.fetchone("SELECT CAST(join_channel AS text), join_message, CAST(leave_channel AS text), leave_message FROM guildconfig_joinleave WHERE guild=?", (guild.id,))
            return quart.jsonify({"data":joinleave_raw, "returnMessage":f"Successfully disabled {choice} messages" if channel == 0 or message.replace(" ", "") == "" else f"Successfully set {choice} message to '{data['message']}'"})

        return quart.jsonify({"error":"Missing perms"})

    @app.route('/api/dashboard/setEvents', methods=['POST'])
    async def setEvents():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")
        
        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))

        print(data)

        if member.guild_permissions.manage_guild:
            if len(data["events"]) > 10:
                return quart.jsonify({"error":"You have hit the maximum amount of events for the server (10)!"})
            
            for event_raw in data["events"]:
                exists = await hc.db.fetchone("SELECT what FROM events WHERE guild=? AND amount=? AND what=? AND action=?", (guild.id, int(event_raw["amount"]), event_raw["what"], event_raw["action"]))
                print(event_raw, exists)
                if not exists:
                    await hc.db.execute("INSERT INTO events VALUES(?, ?, ?, ?)", (guild.id, int(event_raw["amount"]), event_raw["what"], event_raw["action"]))
            
            for event in await hc.db.fetchall("SELECT amount, what, action FROM events WHERE guild=?", (guild.id,)):
                if {"amount":str(event[0]), "what":event[1], "action":event[2]} not in data["events"]:
                    print("not in")
                    await hc.db.execute("DELETE FROM events WHERE guild=? AND amount=? AND what=? AND action=?", (guild.id, event[0], event[1], event[2])) 

            eventsText = "_ _ "
            counter = 0
            for event in data["events"]:
                counter += 1
                eventsText += f"{counter}. At **{event['amount']} {event['what']}**, **{event['action']}**.\n"

            # Log update if available
            embed = discord.Embed(title="Events updated", color=var.embed, timestamp=datetime.datetime.now())
            embed.add_field(name="Events:", value=eventsText, inline=False)
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

            bot.loop.create_task(functions.log(hc, "dashboardUse", guild, embed))

            return quart.jsonify({"returnMessage":"Successfully set events"})
        
        return quart.jsonify({"error":"Missing perms"})

    @app.route('/api/dashboard/setCustomCommands', methods=['POST'])
    async def setCustomCommands():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")

        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))

        commands_raw = await hc.db.fetchall("SELECT name, value FROM custom_commands WHERE guild=?", (guild.id,))

        if member.guild_permissions.manage_guild:
            if len(data["commands"]) > 10:
                return quart.jsonify({"error":"You have hit the maximum amount of custom commands for the server (10)!"})
            
            error_command_empty = False
            
            for command_raw in commands_raw:
                if command_raw not in data["commands"]:
                    await hc.db.execute("DELETE FROM custom_commands WHERE guild=? AND name=?", (guild.id, command_raw[0]))

            for command_name, command_value in data["commands"].items():
                if command_name.replace(" ", "") == "" or command_value.replace(" ", "") == "":
                    error_command_empty = True
                    continue

                exists = await hc.db.fetchone("SELECT name FROM custom_commands WHERE guild=? AND name=? AND value=?", (guild.id, command_name, command_value))
                
                if not exists:
                    name_exists = await hc.db.fetchone("SELECT name FROM custom_commands WHERE guild=? AND name=?", (guild.id, command_name))

                    if not name_exists:
                        await hc.db.execute("INSERT INTO custom_commands VALUES (?, ?, ?)", (guild.id, command_name, command_value))
                    else:
                        await hc.db.execute("UPDATE custom_commands SET value=? WHERE guild=? AND name=?", (command_value, guild.id, command_name))

            commands_raw = await hc.db.fetchall("SELECT name, value FROM custom_commands WHERE guild=?", (guild.id,))
            
            bot.loop.create_task(customCommands.sync_custom_commands(hc, guild=guild))

            # Log update if available
            embed = discord.Embed(title="Custom Commands updated", color=var.embed, timestamp=datetime.datetime.now())
            embed.add_field(name="Commands:", value=f"Too many to send here. View them on the [Web Dashboard]({var.address}#dashboard)", inline=False)
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

            bot.loop.create_task(functions.log(hc, "dashboardUse", guild, embed))
            
            if error_command_empty:
                return quart.jsonify({"error":"One or more of your custom command names or responses were empty! Removed them.", "commands":commands_raw})

            return quart.jsonify({"returnMessage":"Successfully set commands. This may take up to a minute to refresh.", "commands":commands_raw})
        
        return quart.jsonify({"error":"Missing perms", "commands":commands_raw})

    @app.route('/api/dashboard/delWarn', methods=['POST'])
    async def delWarn():
        try:
            user = quart.request.cookies.get('user').split(";;;;")
            user_id = encryption.decode(user[1], var.encryption_key)
        except AttributeError:
            return quart.redirect("/login")
        
        data = await quart.request.json
        guild = bot.get_guild(int(data['guild']))
        member = guild.get_member(int(user_id))
        if member.guild_permissions.manage_messages:
            await hc.db.execute("DELETE FROM warns WHERE guild=? AND id=?", (guild.id, data["id"]))
            
            warns = {
                "returnMessage":f"Successfully deleted warn {data['id']}",
                "warns":await hc.db.fetchall("SELECT id, user, time, mod, reason FROM warns WHERE guild=?", (guild.id,))
            }

            # Log update if available
            embed = discord.Embed(title="Warn deleted (from dashboard)", color=var.embedFail, timestamp=datetime.datetime.now())
            embed.add_field(name="User:", value=f"<@{data['member']}>", inline=False)
            embed.add_field(name="Moderator", value=str(member))
            embed.set_author(name=f"User: {member}", icon_url=member.avatar.url if member.avatar else None)

            bot.loop.create_task(functions.log(hc, "warns", guild, embed))

            return quart.jsonify(warns)

        return quart.jsonify({"error":"Missing perms"})


    def dir_last_updated(folder):
        try:
            return str(max(os.path.getmtime(os.path.join(root_path, f)) for root_path, dirs, files in os.walk(folder) for f in files))
        except ValueError:
            pass

    return app
