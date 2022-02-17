from flask import Flask, render_template, Markup, request, send_from_directory, redirect, make_response, jsonify
from threading import Thread
import os, time, json, base64
from setup import var
from webserver.oauth import Oauth as oauth
from functions import functions, encryption
from functions import functions, customCommands
import discord 
import datetime
import resources

loggingOptions = ["channelCreate", "channelDelete", "roleCreate", "roleDelete", "nicknameChange", "dashboardUse", "warns"]
encryptionKey = os.environ.get("encryptionKey")

bot : discord.Bot = None

def webserver_run(client):
    t = Thread(target=run)
    t.start()
    global bot 
    bot = client

app = Flask(__name__, template_folder="./webserver/templates/")
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
#app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route('/static/css/<path:filename>')
def custom_static(filename):
    return send_from_directory('webserver/Static/static/css/', filename)

@app.route('/static/js/<path:filename>')
def custom_js(filename):
    return send_from_directory('webserver/Static/static/js/', filename)

@app.route('/static/images/<path:filename>')
def custom_image(filename):
    return send_from_directory('webserver/Static/static/images/', filename)

@app.route('/')
def home():
    return render_template('index.html', last_updated=dir_last_updated('/static'))

@app.route('/about')
def about():
    return render_template('about.html', last_updated=dir_last_updated('/static'))

@app.route('/changelogs')
def changelogs():
    return render_template('changelogs.html', last_updated=dir_last_updated('/static'))

@app.route('/invite')
def invite():
    return redirect(var.invite)

@app.route('/support')
def support():
    return redirect(var.server)

@app.route('/invited')
def invited():
    if request.args.get("guild_id") == None:
        return redirect("/")
    guildName = bot.get_guild(int(request.args['guild_id'])) if bot.get_guild(int(request.args['guild_id'])) else "None"
    return render_template('invited.html', last_updated=dir_last_updated('/static'), guild_name=guildName)

@app.route('/api/changelogs', methods=['GET'])
def changelogsAPI():
    changelogs = {}
    for file in [f for f in os.listdir("./resources/changelogs/") if os.path.isfile(os.path.join("./resources/changelogs/", f))]:
        with open("resources/changelogs/" + file) as f:
            changelogs[file.replace(".txt", "")] = f.read()

    return jsonify(changelogs)

@app.route('/api/commands', methods=['GET'])
def commandsAPI():
    commands = []
    done = []

    for command in bot.commands:
        if command.name not in done:
            done.append(command.name)
            category = None 
            for categoryIter in resources.commands.json:
                if command.name in resources.commands.json[categoryIter]:
                    category = categoryIter

            options = [{"name":option.name, "description":option.description, "required":option.required} for option in command.options]

            if category:
                commands.append({"name":command.name, "description":command.description, "options":options, "category":category})
    
    return jsonify(commands)

@app.route('/api/userinfo', methods=['GET'])
def userinfoAPI():
    try:
        user = request.cookies.get('user').split(";;;;")
        id = encryption.decode(user[1], encryptionKey)
        name = encryption.decode(user[2], encryptionKey)
        avatar = encryption.decode(user[3], encryptionKey)
        user = bot.get_user(int(id))
    except:
        return jsonify({"user":None, "type":"unknown"})
    
    if not user:
        return jsonify({
            "user":{
                "id":id,
                "name":name,
                "avatar":avatar
            }, 
            "type":"user"
        })
    else:
        return jsonify({
            "user":{
                "id":str(user.id),
                "name":user.name,
                "avatar":user.avatar.url,
                "mutual":[{"id":str(guild.id), "name":guild.name, "icon":guild.icon.url} for guild in bot.guilds if guild.get_member(int(user.id))]
            }, 
            "type":"mutual"
        })



@app.route("/login", methods=["GET"])  
def admin():
    try:
        code = request.args['code']
        print(code)
        access_token=oauth.get_access_token(code)
        print(access_token)
        user_json = oauth.get_user_json(access_token)
        print(user_json)
    except Exception as e:
        print(e)
        return redirect(var.login)
    try:
        
        id = user_json["id"]
        user = bot.get_user(int(id))
        resp = make_response(redirect("/#dashboard"))
        cookiestring = ''
        cookiestring = cookiestring + ';;;;' + encryption.encode(str(user_json['id']), encryptionKey).decode("utf-8")
        cookiestring = cookiestring + ';;;;' + encryption.encode(str(user_json['username']), encryptionKey).decode("utf-8")
        cookiestring = cookiestring + ';;;;' + encryption.encode(str(user_json['avatar']), encryptionKey).decode("utf-8")
        resp.set_cookie('user', cookiestring, max_age=8_760*3600)
        return resp
    except Exception as e:
        print(e)
        return redirect("/")

@app.route('/dashboard')
def dashboard():
    try:
        user = request.cookies.get('user').split(";;;;")
        id = encryption.decode(user[1], encryptionKey)
        name = encryption.decode(user[2], encryptionKey)
    except:
        resp = make_response(redirect("/login"))
        resp.set_cookie('user', '', expires=0)
        return resp
    return render_template('dashboard.html', last_updated=dir_last_updated('/static'))

@app.route('/dashboard/<server>')
def dashboardWith(server):
    try:
        user = request.cookies.get('user').split(";;;;")
        id = encryption.decode(user[1], encryptionKey)
        name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")
    return render_template('dashboard.html', last_updated=dir_last_updated('/static'))

def jsonifyB(data, status=200, indent=4, sort_keys=True):
    response = make_response(json.dumps(dict(data), indent=indent, sort_keys=sort_keys))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['mimetype'] = 'application/json'
    response.status_code = status
    return response


@app.route('/api/dashboard/serverDatabase')
def serverDataAPI():
    args = request.args
    value = {}
    try:
        user = request.cookies.get('user').split(";;;;")
        user_id = encryption.decode(user[1], encryptionKey)
        user_name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")
    warns = functions.read_data_sync('databases/warns.json')
    warnsString = json.dumps(warns)
    events = functions.read_data_sync("databases/events.json")
    music = functions.read_data_sync("databases/music.json")
    
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
                "prefix":functions.prefix(guild),
                "joinleave":joinleaveData[str(guild.id)] if str(guild.id) in joinleaveData else {},
                "music":music[str(guild.id)] if str(guild.id) in music else {},
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
        return jsonifyB(value)
    return jsonify(value)

@app.route('/api/dashboard/setAutorole', methods=['POST'])
def setAutorole():
    try:
        user = request.cookies.get('user').split(";;;;")
        user_id = encryption.decode(user[1], encryptionKey)
        user_name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")

    with open("databases/setup.json") as f:
        joinleave = json.load(f)

    data = request.json
    guild = bot.get_guild(int(data['guild']))
    member = guild.get_member(int(user_id))

    try:
        role = data["role"]
    except:
        return jsonify({"error":"Invalid role"})
    
    if member.guild_permissions.manage_guild:
        if str(guild.id) not in joinleave:
            joinleave[str(guild.id)] = {}
        if role == "None" and "autorole" in joinleave[str(guild.id)]:
            what = "removed"
            del joinleave[str(guild.id)]["autorole"]
        elif role == "None":
            what = "removed"
            pass 
        else:
            what = "set"
            joinleave[str(guild.id)]["autorole"] = str(role)
        functions.save_data_sync("databases/setup.json", joinleave)
        functions.read_load_sync("databases/setup.json", joinleave)

        # Log update if available
        embed = discord.Embed(title="Autorole role updated", color=var.embed, timestamp=datetime.datetime.now())
        embed.add_field(name="New:", value=guild.get_role(int(role)).mention, inline=False)
        embed.set_author(name=f"User: {member}", icon_url=member.avatar.url)

        bot.loop.create_task(functions.log(bot, "dashboardUse", guild, embed))
            
        return jsonify({"data":joinleave[str(guild.id)], "returnMessage":f"Successfully {what} autorole role"})
    else:
        return jsonify({"error":"Missing perms"})

@app.route('/api/dashboard/setLogging', methods=['POST'])
def setLogging():
    try:
        user = request.cookies.get('user').split(";;;;")
        user_id = encryption.decode(user[1], encryptionKey)
        user_name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")

    with open("databases/setup.json") as f:
        joinleave = json.load(f)

    data = request.json
    guild = bot.get_guild(int(data['guild']))
    member = guild.get_member(int(user_id))

    try:
        loggingData = data["logging"]
    except:
        return jsonify({"error":"Invalid role"})
    
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
        embed.set_author(name=f"User: {member}", icon_url=member.avatar.url)

        bot.loop.create_task(functions.log(bot, "dashboardUse", guild, embed))

        functions.save_data_sync("databases/setup.json", joinleave)
        functions.read_load_sync("databases/setup.json", joinleave)
            
        return jsonify({"data":joinleave[str(guild.id)], "returnMessage":f"Successfully set logging settings"})
    else:
        return jsonify({"error":"Missing perms"})

@app.route('/api/dashboard/setMessage', methods=['POST'])
def setMessage():
    try:
        user = request.cookies.get('user').split(";;;;")
        user_id = encryption.decode(user[1], encryptionKey)
        user_name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")
    
    with open("databases/setup.json") as f:
        joinleave = json.load(f)

    data = request.json
    guild = bot.get_guild(int(data['guild']))
    member = guild.get_member(int(user_id))

    try:
        channel = int(data["channel"])
        message = data["message"]
        choice = data["type"]
    except:
        return jsonify({"error":"Invalid channel/message"})
    
    if member.guild_permissions.manage_guild:
        if message.replace(" ", "") == "" and str(guild.id) in joinleave and choice in joinleave[str(guild.id)]:
            del joinleave[str(guild.id)][choice]
        elif message.replace(" ", "") == "" and (str(guild.id) not in joinleave or choice not in joinleave[str(guild.id)]):
            pass
        elif len(message) > 1900:
            return jsonify({"error":"Message over 1900 characters"})
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

        return jsonify({"data":joinleave[str(guild.id)], "returnMessage":f"Successfully set {choice} message to '{data['message']}'"})
    else:
        return jsonify({"error":"Missing perms"})
        

@app.route('/api/dashboard/setPrefix', methods=['POST'])
def setPrefix():
    try:
        user = request.cookies.get('user').split(";;;;")
        user_id = encryption.decode(user[1], encryptionKey)
        user_name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")
    prefixes = functions.read_data_sync("databases/prefixes.json")
    data = request.json
    guild = bot.get_guild(int(data['guild']))
    member = guild.get_member(int(user_id))
    if member.guild_permissions.manage_guild:
        if len(data['prefix']) > 50:
            return jsonify({"error":"Prefix must be under 50 characters"})
        if data['prefix'] != var.prefix and data['prefix'] != 'reset' and data['prefix'].replace(" ", "") != "":
            prefixes[str(guild.id)] = data['prefix']
            returnPrefix = data['prefix']
            returnMess = f"Successfully set prefix to {data['prefix']}"
        elif str(guild.id) in prefixes:
            del prefixes[str(guild.id)]
            returnPrefix = var.prefix
            returnMess = "Successfully reset prefix"
        else:
            returnPrefix = var.prefix
            returnMess = "Successfully reset prefix"
        functions.save_data_sync("databases/prefixes.json", prefixes)
        functions.read_load_sync("databases/prefixes.json", prefixes)

        

        return jsonify({"prefix":returnPrefix, "returnMessage":returnMess})
    else:
        return jsonify({"error":"Missing perms"})

@app.route('/api/dashboard/setEvents', methods=['POST'])
def setEvents():
    try:
        user = request.cookies.get('user').split(";;;;")
        user_id = encryption.decode(user[1], encryptionKey)
        user_name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")
    events = functions.read_data_sync("databases/events.json")
    data = request.json
    guild = bot.get_guild(int(data['guild']))
    member = guild.get_member(int(user_id))
    if member.guild_permissions.manage_guild:
        if len(data["events"]) > 10:
            return jsonify({"error":"You have hit the maximum amount of events for the server (10)!"})
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
        embed.set_author(name=f"User: {member}", icon_url=member.avatar.url)

        bot.loop.create_task(functions.log(bot, "dashboardUse", guild, embed))

        return jsonify({"returnMessage":"Successfully set events"})
    else:
        return jsonify({"error":"Missing perms"})

@app.route('/api/dashboard/setCustomCommands', methods=['POST'])
def setCustomCommands():
    try:
        user = request.cookies.get('user').split(";;;;")
        user_id = encryption.decode(user[1], encryptionKey)
        user_name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")

    commands = functions.read_data_sync("databases/commands.json")

    data = request.json
    guild = bot.get_guild(int(data['guild']))
    member = guild.get_member(int(user_id))

    if member.guild_permissions.manage_guild:
        if len(data["commands"]) > 10:
            return jsonify({"error":"You have hit the maximum amount of custom commands for the server (10)!"})
        
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
            if cmd in var.musicCommands:
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

        
        bot.loop.create_task(customCommands.doGuildCustomCommands(bot, guild.id, commands[str(guild.id)]))

        # Log update if available
        embed = discord.Embed(title="Custom Commands updated", color=var.embed, timestamp=datetime.datetime.now())
        embed.add_field(name="Commands:", value=f"Too many to send here. View them on the [Web Dashboard]({var.address}#dashboard)", inline=False)
        embed.set_author(name=f"User: {member}", icon_url=member.avatar.url)

        bot.loop.create_task(functions.log(bot, "dashboardUse", guild, embed))
        

        if did == True:
            return jsonify({"error":"One or more of your custom commands already exist! Removed them.", "commands":commands[str(guild.id)]})
        if did2 == True:
            return jsonify({"error":"One or more of your custom commands were empty! Removed them.", "commands":commands[str(guild.id)]})

        return jsonify({"returnMessage":"Successfully set commands. This may take up to a minute to refresh.", "commands":commands[str(guild.id)]})
    else:
        return jsonify({"error":"Missing perms", "commands":commands[str(guild.id)]})

@app.route('/api/dashboard/delWarn', methods=['POST'])
def delWarn():
    try:
        user = request.cookies.get('user').split(";;;;")
        user_id = encryption.decode(user[1], encryptionKey)
        user_name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")
    warns = functions.read_data_sync("databases/warns.json")
    data = request.json
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
        embed.set_author(name=f"User: {member}", icon_url=member.avatar.url)

        bot.loop.create_task(functions.log(bot, "warns", guild, embed))

        return jsonify(warns)
    else:
        return jsonify({"error":"Missing perms"})

@app.route('/api/dashboard/setMusic', methods=['POST'])
def setMusic():
    try:
        user = request.cookies.get('user').split(";;;;")
        user_id = encryption.decode(user[1], encryptionKey)
        user_name = encryption.decode(user[2], encryptionKey)
    except:
        return redirect("/login")
    music = functions.read_data_sync("databases/music.json")
    data = request.json
    guild = bot.get_guild(int(data['guild']))
    member = guild.get_member(int(user_id))
    del data["guild"]

    if member.guild_permissions.manage_guild:
        if str(guild.id) not in music:
            music[str(guild.id)] = {}
        music[str(guild.id)] = data 

        functions.save_data_sync("databases/music.json", music)

        return jsonify({"returnMessage":"Successfully set music permissions"})
    else:
        return jsonify({"error":"Missing perms"})


def dir_last_updated(folder):
    try:
        return str(max(os.path.getmtime(os.path.join(root_path, f))
                    for root_path, dirs, files in os.walk(folder)
                    for f in files))
    except:
        return 0

from gevent.pywsgi import WSGIServer

def run():
    http = WSGIServer(('0.0.0.0', 5000), app) 
    http.serve_forever()
    #app.run(host='0.0.0.0',port=5000)

run()

