
guilds = [447702058162978827]

musicCommands = ["connect", "play", "pause", "stop", "resume", "skip", "queue", "now_playing", "volume", "musicping", "join", "summon", "shut", "q", "playlist", "np", "current", "currentsong", "playingnow", "playing", "vol", "leave", "disconnect", "die", "musicuptime", "loop"]

embed=0xFF8700
embedSuccess=0x00FF00
embedFail=0xFF0000

version = "1.0.0"
prefix="/"
owner=368071242189897728

address = "http://localhost:5000"

login = None
invite = None

server = "https://discord.gg/HChmbSN"
topgg = "https://top.gg/bot/486180321444888586"
website = address

botAdmins = [368071242189897728, 444176530357354527, 449662597927665666]

def get_client(client):
    global login 
    global invite 

    login = f"https://discord.com/api/oauth2/authorize?client_id={client.user.id}&redirect_uri={address}/login&response_type=code&scope=identify%20guilds"

    invite = f"https://discord.com/api/oauth2/authorize?client_id={client.user.id}&permissions=0&redirect_uri={address}/invited&response_type=code&scope=bot%20applications.commands"