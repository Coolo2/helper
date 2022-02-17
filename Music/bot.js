const discord = require("discord.js-light");
const youtube = require("youtube-sr").default;
const functions = require("./functions.js")
const classes = require("./classes")
const ytdl = require("discord-ytdl-core")
const genius = require("genius-lyrics");
const dotenv = require("dotenv")

dotenv.config()

const axios = require("axios").default

const voice = require("@discordjs/voice")
const lyricsClient = new genius.Client();

process.env.UV_THREADPOOL_SIZE = 128;

process.on('uncaughtException', function (err) {
    console.log('Caught exception: ', err.lineNumber);
});

const bot = new discord.Client({
    makeCache: discord.Options.cacheWithLimits({
        ApplicationCommandManager: Infinity, // guild.commands
        BaseGuildEmojiManager: Infinity, // guild.emojis
        ChannelManager: Infinity, // client.channels
        GuildChannelManager: Infinity, // guild.channels
        GuildBanManager: Infinity, // guild.bans
        GuildInviteManager: Infinity, // guild.invites
        GuildManager: Infinity, // client.guilds
        GuildMemberManager: Infinity, // guild.members
        GuildStickerManager: Infinity, // guild.stickers
        MessageManager: Infinity, // channel.messages
        PermissionOverwriteManager: Infinity, // channel.permissionOverwrites
        PresenceManager: 0, // guild.presences
        ReactionManager: Infinity, // message.reactions
        ReactionUserManager: Infinity, // reaction.users
        RoleManager: Infinity, // guild.roles
        StageInstanceManager: Infinity, // guild.stageInstances
        ThreadManager: Infinity, // channel.threads
        ThreadMemberManager: Infinity, // threadchannel.members
        UserManager: Infinity, // client.users
        VoiceStateManager: Infinity // guild.voiceStates
    }),
    intents: [ discord.Intents.FLAGS.GUILD_MEMBERS, discord.Intents.FLAGS.GUILD_VOICE_STATES],
});

permissionsAll = "MOVE_MEMBERS"
errors = new functions.Errors()
guilds = {}

async function getMusicPermissions(guildId) {
    url = `https://helperdata.glitch.me/view${process.env.databaseToken}/databases/music.json`

    data = (await axios.get(url)).data;
    guildData = data[guildId]
    if (!guildData) guildData = {}
    
    if (!guildData.permissions) {
        guildData.permissions = permissionsAll
    }

    return guildData
}

bot.on("ready", async function() {
    console.log(bot.user.tag + " online")
})

async function doVotes(type, member, musicPermissions, permissions, guildId, ) {
    if (!guilds[guildId].votes[type]) {guilds[guildId].votes[type] = {}}

    mGuild = guilds[guildId]
    voted = false
    vcMembers = 0

    for (memberM of member.voice.channel.members) {
        if (!memberM[1].user.bot && !memberM[1].voice.deaf) {vcMembers += 1}
    }

    // Calculate required votes
    required = Math.ceil(vcMembers / 2)
    length = Object.keys(guilds[guildId].votes[type]).length + 1

    if (mGuild.queue[0].requestor.id == member.id) {
        // The member requested the song. Continue
    } else if (permissions.has(musicPermissions.permissions)) {
        // The member has valid permissions. Continue
    } else if (vcMembers < 3) {
        // There are less than 3 people in the voice channel. Do not require skip votes
    } else {
        // The member does not have permission and did not request the song. Initiate voting.
        voted = true 
        inFile = false
        
        if (!mGuild.votes[type]) guilds[guildId].votes[type] = {}
        if (guilds[guildId].votes[type][member.user.id]) inFile = true
        guilds[guildId].votes[type][member.user.id] = true 

        if (inFile) {
            length -= 1
            return {
                do:false,
                voted:false,
                votes:length,
                required:required
            }
        }

        if (length >= required) {
            guilds[guildId].votes[type] = {}
        } else {
            
            return {
                do:false,
                voted:true,
                votes:length,
                required:required
            }
        }
    }

    return {
        do: true,
        voted:voted,
        votes:length,
        required:required
    }
}

function calculateFilters(filters) {
    filtersArr = ["-af"]

    if (filters.pitch) {
        if (filters.speed) {
            filtersArr.push(`asetrate=48000*2^(${filters.pitch}/12),atempo=${filters.speed/100}`)
        } else {
            filtersArr.push(`asetrate=48000*2^(${filters.pitch}/12),atempo=1/2^(${filters.pitch}/12)`)
        }
    } else if (filters.bass) {
        filtersArr.push(`bass=g=${filters.bass/100}`)
    }
    if (filters.speed && !filters.pitch) {
        filtersArr.push(`atempo=${filters.speed/100}`)
    }

    if (filtersArr.length == 1) {
        filtersArr = []
    }

    return filtersArr
}

async function playLoop(guild) {
    mGuild = guilds[guild.id]
    mGuild.stream = ytdl(
        mGuild.queue[mGuild.index].video.id, 
        {
            seek: mGuild.queue[mGuild.index].seek,
            filter: "audioonly",
            highWaterMark: 1 << 25,
            opusEncoded: true,
            encoderArgs:calculateFilters(mGuild.filters)
        }
    )

    mGuild.player = voice.createAudioPlayer();
    mGuild.resource = voice.createAudioResource(mGuild.stream, { inlineVolume: true })

    try {
        mGuild.connection = await voice.joinVoiceChannel({
            channelId:mGuild.voiceChannel.id,
            guildId:mGuild.guild.id,
            adapterCreator: mGuild.guild.voiceAdapterCreator
        })
        
    } catch {
        await mGuild.playInteraction.reply({embeds:[functions.getEmbed(errors.VoicePermissions)]})
        await guilds[guild.id].stop()
        return
    }


    await mGuild.player.play(mGuild.resource)
    mGuild.connection.subscribe(mGuild.player)
    mGuild.startedAt = new Date()
    mGuild.startedTime = mGuild.queue[mGuild.index].seek

    mGuild.player.addListener("stateChange", async function(oldOne, newOne) {
        if (newOne.status == "idle") {
            await mGuild.skip()

            if (guilds[guild.id]) {
                embed = await getNowPlaying(guild.id)
                message = await guilds[guild.id].textChannel.send({embeds:[embed]})

                if (guilds[guild.id].nowPlayingMessage) {await guilds[guild.id].nowPlayingMessage.delete()}
                guilds[guild.id].nowPlayingMessage = message
            } else {
                try{
                    await mGuild.textChannel.send(
                        {
                            embeds:[functions.getEmbed(
                                "Queue ended", 
                                `The queue for this server ended. Left the voice channel.`)
                            ]
                        }
                    )
                } catch{} 
            }
            
        }
    })
}

// {search:[{name:"responseName", value:"responseValue (URL)"}]}
// reduces search load
songCache = {

}

async function autocomplete_play(interaction) {
    if (!interaction.member.voice.channelId) {
        return interaction.respond([{name:"Please join a voice channel in this server. If you are in one, leave and rejoin.", value:""}])
    }

    if (interaction.options.getString("song")) {
        if (interaction.options.getString("song").length > 2 ) {
            
            if (songCache[interaction.options.getString("song")]) {
                return interaction.respond(songCache[interaction.options.getString("song")])
            }
            try{
                search = await youtube.search(interaction.options.getString("song"), { limit: 5 })  

                response = [] 
                for (video of search) {
                    response.push({name:video.title, value:`https://youtube.com/watch?v=${video.id}`})
                }
                songCache[interaction.options.getString("song")] = response
                return interaction.respond(response)
            } catch{console.log("ERR ON SEARCH")}
        } else {
            return interaction.respond([{name:"Please type at least 3 characters to show results. Otherwise send without clicking a result", value:""}])
        }
    } else  {
        return interaction.respond([{name:"Please type at least 3 characters to show results. Otherwise send without clicking a result", value:""}])
    }
}
bot.on('interactionCreate', async interaction => {

    if (interaction.isAutocomplete()) {
        if (interaction.commandName == "play") {
            await autocomplete_play(interaction)
        }
        if (interaction.commandName == "skipto") {
            await autocomplete_queueItem(interaction, "track")
        }
        if (interaction.commandName == "remove") {
            await autocomplete_queueItem(interaction, "track", ignoreFirst=true)
        }
    }
	if (interaction.isCommand()) {
        if (interaction.commandName == "play") {
            await command_play(interaction)
        }
        if (interaction.commandName == "stop") {
            await command_stop(interaction)
        }
        if (interaction.commandName == "skip") {
            await command_skip(interaction)
        }
        if (interaction.commandName == "now-playing") {
            await command_nowplaying(interaction)
        }
        if (interaction.commandName == "queue") {
            await command_queue(interaction)
        }
        if (interaction.commandName == "back") {
            await command_back(interaction)
        }
        if (interaction.commandName == "volume") {
            await command_volume(interaction)
        }
        if (interaction.commandName == "pause") {
            await command_pause(interaction)
        }
        if (interaction.commandName == "resume") {
            await command_resume(interaction)
        }
        if (interaction.commandName == "seek") {
            await command_seek(interaction)
        }
        if (interaction.commandName == "lyrics") {
            await command_lyrics(interaction)
        }
        if (interaction.commandName == "skipto") {
            await command_skipto(interaction)
        }
        if (interaction.commandName == "remove") {
            await command_remove(interaction)
        }
        if (interaction.commandName == "restart") {
            await command_restart(interaction)
        }
        if (interaction.commandName == "loop") {
            await command_loop(interaction)
        }
        if (interaction.commandName == "filter") {
            await command_filter(interaction)
        }
    }
    
});

async function autocomplete_queueItem(interaction, argName, ignoreFirst=false) {
    mGuild = guilds[interaction.guild.id]

    if (!mGuild) {
        return interaction.respond([{name:"Nothing is playing in this server!", value:""}])
    }
    options = []
    counter = 0
    for (video of mGuild.queue) {
        counter += 1
        if (ignoreFirst && counter < 2) continue 
        if (interaction.options.getString(argName) && !`${counter}. ${video.video.title}`.toLowerCase().includes(interaction.options.getString(argName).toLowerCase())) {
            continue
        }
        
        options.push({name:`${counter}. ${video.video.title}`, value:counter.toString()})
    }
    return interaction.respond(options)
}

async function command_skipto(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})

    musicPermissions = await getMusicPermissions(interaction.guild.id)

    if (!musicPermissions.commands || !musicPermissions.commands.skipto) {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    }
    

    track = interaction.options.getString("track")

    if (isNaN(track)) {
        return interaction.reply({embeds:[functions.getErrorEmbed(`Could not find valid track/index from \`${track}\`... Maybe try use the options provided?`)]})
    }
    track = parseInt(track)
    index = track - 1

    if (index > guilds[interaction.guild.id].queue.length) {
        return interaction.reply({embeds:[functions.getErrorEmbed(`Could not find valid track/index from \`${track}\`... Maybe try use the options provided?`)]})
    }

    await interaction.deferReply()

    removed = guilds[interaction.guild.id].queue.splice(0, index)

    for (removed of removed) {
        guilds[interaction.guild.id].history.push(removed)
    }

    await guilds[interaction.guild.id].playLoop()

    nowPlaying = await getNowPlaying(interaction.guild.id)

    return await interaction.followUp({embeds:[nowPlaying.setColor("#00FF00")]})
}

async function command_restart(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})
    
    musicPermissions = await getMusicPermissions(interaction.guild.id)

    if (!musicPermissions.commands || !musicPermissions.commands.restart || musicPermissions.commands.restart == "permissions") {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    } else if (musicPermissions.commands.restart == "voting") {
        vote = await doVotes("restart", interaction.member, musicPermissions, interaction.memberPermissions, interaction.guild.id)

        if (!vote.do) {
            if (vote.voted) {
                return await interaction.reply({embeds:[functions.getEmbed(
                    `Voted to restart song (${vote.votes}/${vote.required})`, 
                    `Get more votes and the song will be restarted (others have to do \`/restart\`)`)]}
                )
                
            } else {
                return await interaction.reply({embeds:[functions.getErrorEmbed(
                    `You have already voted to restart! (${vote.votes}/${vote.required})`)]}
                )
            }
        }
    }

    await interaction.deferReply()

    guilds[interaction.guild.id].queue[0].seek = 0

    await guilds[interaction.guild.id].playLoop()

    nowPlaying = await getNowPlaying(interaction.guild.id)

    return await interaction.followUp({embeds:[nowPlaying.setColor("#00FF00")]})
}


async function command_remove(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})

    musicPermissions = await getMusicPermissions(interaction.guild.id)

    if (!musicPermissions.commands || !musicPermissions.commands.remove) {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    }

    track = interaction.options.getString("track")

    if (isNaN(track)) {
        return interaction.reply({embeds:[functions.getErrorEmbed(`Could not find valid track/index from \`${track}\`... Maybe try use the options provided?`)]})
    }
    track = parseInt(track)
    index = track - 1

    if (index > guilds[interaction.guild.id].queue.length) {
        return interaction.reply({embeds:[functions.getErrorEmbed(`Could not find valid track/index from \`${track}\`... Maybe try use the options provided?`)]})
    }

    removed = guilds[interaction.guild.id].queue.splice(index, 1)


    return await interaction.reply({embeds:[
        functions.getSuccessEmbed(`Successfully removed track from queue`, `Removed [${removed[0].video.title}](https://youtube.com/watch?v=${removed[0].video.id}) from queue`)]})
}


function addGuildFunctions(guildId) {
    guilds[guildId].stop = async function() {
        guilds[guildId].connection.destroy()
        delete guilds[guildId]
    }
    guilds[guildId].skip = async function() {
        if (guilds[guildId].queue.length > 1) {
            if (guilds[guildId].loop == "queue") {
                guilds[guildId].index += 1
                if (guilds[guildId].index > (guilds[guildId].queue.length - 1)) {
                    guilds[guildId].index = 0
                }
                
            } else if (guilds[guildId].loop != "track") {
                guilds[guildId].history.push(guilds[guildId].queue[0])
                guilds[guildId].queue.shift()
            }
            
            
            
            await guilds[guildId].playLoop()

            

        } else {
            if (guilds[guildId].loop != "track" && guilds[guildId].loop != "queue") {
                await guilds[guildId].stop()
            } else {
                await guilds[guildId].playLoop()
            }
        }
    }
}

async function command_skip(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})

    if (musicPermissions.commands && musicPermissions.commands.skip == "permissions") {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    } else if (!musicPermissions.commands || !musicPermissions.commands.skip || musicPermissions.commands.skip == "voting") {
        vote = await doVotes("skip", interaction.member, musicPermissions, interaction.memberPermissions, interaction.guild.id)

        if (!vote.do) {
            if (vote.voted) {
                return await interaction.reply({embeds:[functions.getEmbed(
                    `Voted to skip song (${vote.votes}/${vote.required})`, 
                    `Get more votes and the song will be skipped (others have to do \`/skip\`)`)]}
                )
                
            } else {
                return await interaction.reply({embeds:[functions.getErrorEmbed(
                    `You have already voted to skip! (${vote.votes}/${vote.required})`)]}
                )
            }
        }
    }

    skipped = ""
    if (guilds[interaction.guild.id].loop == "track") {
        guilds[interaction.guild.id].loop = null
        skipped = ", disabled loop,"
    }
    if (guilds[interaction.guild.id].loop == "queue") {
        if (guilds[interaction.guild.id].index > 0) {
            for(var i = 0; i < guilds[interaction.guild.id].index; i++){
                guilds[interaction.guild.id].history.push(guilds[interaction.guild.id].queue[0])
                guilds[interaction.guild.id].queue.shift()
            }
        }
        guilds[interaction.guild.id].index = 0
        guilds[interaction.guild.id].loop = null
        skipped = ", disabled loop,"
    }

    await mGuild.skip()

    if (guilds[interaction.guild.id]) {
        nowPlaying = await getNowPlaying(interaction.guild.id)
        if (skipped != "") {
            nowPlaying.setTitle("[Disabled Loop] Now Playing:")
        }
        return await interaction.reply({embeds:[nowPlaying.setColor("#00FF00")]})
    } else {
        return await interaction.reply(
            {
                embeds:[functions.getSuccessEmbed(
                    "Successfully skipped song", 
                    `**Queue ended.** Skipped the song${skipped} and left the voice channel`)
                ]
            }
        )
    }
    
}

async function command_loop(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})

    musicPermissions = await getMusicPermissions(interaction.guild.id)

    if (!musicPermissions.commands || !musicPermissions.commands.loop) {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    }

    if (interaction.options.getString("type") == "off") {
        guilds[interaction.guild.id].loop = null 
    } else {
        guilds[interaction.guild.id].loop = interaction.options.getString("type")
    }

    await interaction.reply({embeds:[functions.getSuccessEmbed(`Successfully set loop`, `Successfully set loop to **${interaction.options.getString("type")}**`)]})
}

async function command_stop(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})

    if (musicPermissions.commands && musicPermissions.commands.stop == "permissions") {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    } else if (!musicPermissions.commands || !musicPermissions.commands.stop || musicPermissions.commands.stop == "voting") {
        vote = await doVotes("stop", interaction.member, musicPermissions, interaction.memberPermissions, interaction.guild.id)

        if (!vote.do) {
            if (vote.voted) {
                return await interaction.reply({embeds:[functions.getEmbed(
                    `Voted to stop song (${vote.votes}/${vote.required})`, 
                    `Get more votes and the song will be stopped (others have to do \`/stop\`)`)]}
                )
                
            } else {
                return await interaction.reply({embeds:[functions.getErrorEmbed(
                    `You have already voted to stop! (${vote.votes}/${vote.required})`)]}
                )
            }
        }
    }

    mGuild = guilds[interaction.guild.id]

    await guilds[interaction.guild.id].stop()

    return await interaction.reply(
        {
            embeds:[functions.getSuccessEmbed(
                "Successfully stopped player", 
                `Stopped playing **[${mGuild.queue[0].video.title}](https://youtube.com/watch?v=${mGuild.queue[0].video.id})** in **<#${mGuild.voiceChannel.id}>**`)
            ]
        }
    )
}


async function command_play(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})

    musicPermissions = await getMusicPermissions(interaction.guild.id)

    if (musicPermissions.commands && musicPermissions.commands.play) {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    }

    try{voiceChannel = await bot.channels.fetch(interaction.member.voice.channelId)} catch{
        return await interaction.reply({embeds:[functions.getErrorEmbed(errors.VoicePermissions)]})
    }

    await interaction.deferReply()

    search = []

    if (interaction.options.getString("song").includes("youtu")) {
        try{
            info = await ytdl.getInfo(interaction.options.getString("song"))
            var minutes = Math.floor(info.videoDetails.lengthSeconds / 60);
            var seconds = info.videoDetails.lengthSeconds - minutes * 60;

            search = [{
                title:info.videoDetails.title, 
                id:info.videoDetails.videoId, 
                thumbnail:{url:`https://img.youtube.com/vi/${info.videoDetails.videoId}/0.jpg`},
                duration:info.videoDetails.lengthSeconds*1000,
                durationFormatted:`${minutes}:${seconds.toString().padStart(2, "0")}`
            }]
        } catch {
            search = await youtube.search(interaction.options.getString("song"), { limit: 1 })
        }
    } else {
        search = await youtube.search(interaction.options.getString("song"), { limit: 1 })
    }

    if (search.length == 0) {
        return await interaction.followUp({embeds:[functions.getErrorEmbed(errors.NoSongFound)]})
    }

    if (!interaction.options.getInteger("seek")) {seek = 0} else {seek = interaction.options.getInteger("seek")}

    queueData = {video:search[0], search:interaction.options.getString("song"), requestor:interaction.member, seek:seek}

    if (!(guilds[interaction.guild.id])) {
        guilds[interaction.guild.id] = new classes.musicGuild(bot, interaction.guild)
        guild = guilds[interaction.guild.id]

        guild.queue = []
        guild.voiceChannel = voiceChannel
        guild.textChannel = interaction.channel
        guild.index = 0
        guild.history = []
        guild.votes = {}
        guild.nowPlayingMessage = undefined
        guild.loop = null // "song" for song loop "queue" for whole queue loop
        guild.playInteraction = interaction
        guild.filters = {}
        addGuildFunctions(interaction.guild.id)


        guild.queue.push(queueData)

        guild.playLoop = async function() {await playLoop(interaction.guild)}

        await guild.playLoop()
    } else {
        guild = guilds[interaction.guild.id]
        guild.queue.push(queueData)
    }

    
    nowPlaying = await getNowPlaying(interaction.guild.id, index=guild.queue.length-1)

    return await interaction.followUp({embeds:[nowPlaying.setColor("#00FF00")]})
    
}

async function command_back(interaction) {
    mGuild = guilds[interaction.guild.id]
    
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})
    if (!mGuild.history || mGuild.history.length == 0) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NoBack)]})

    if (musicPermissions.commands && musicPermissions.commands.back == "permissions") {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    } else if (!musicPermissions.commands || !musicPermissions.commands.back || musicPermissions.commands.back == "voting") {
        vote = await doVotes("back", interaction.member, musicPermissions, interaction.memberPermissions, interaction.guild.id)

        if (!vote.do) {
            if (vote.voted) {
                return await interaction.reply({embeds:[functions.getEmbed(
                    `Voted to go back (${vote.votes}/${vote.required})`, 
                    `Get more votes and the player will go back (others have to do \`/back\`)`)]}
                )
                
            } else {
                return await interaction.reply({embeds:[functions.getErrorEmbed(
                    `You have already voted to go back! (${vote.votes}/${vote.required})`)]}
                )
            }
        }
    }

    await interaction.deferReply()

    popped = guilds[interaction.guild.id].history.pop()
    item = guilds[interaction.guild.id].queue[0]
    guilds[interaction.guild.id].queue.splice(0, 1);

    guilds[interaction.guild.id].queue.unshift(popped, item)

    await guilds[interaction.guild.id].playLoop()

    nowPlaying = await getNowPlaying(interaction.guild.id)
    return await interaction.followUp({embeds:[nowPlaying.setColor("#00FF00")]})
}

async function command_nowplaying(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})

    nowPlaying = await getNowPlaying(interaction.guild.id)

    return await interaction.reply({embeds:[nowPlaying.setColor("#00FF00")]})
}

async function command_lyrics(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})

    mGuild = guilds[interaction.guild.id]

    await interaction.deferReply()

    try {
        searches = await lyricsClient.songs.search(mGuild.queue[0].video.title);
    } catch {
        return interaction.followUp({embeds:[functions.getErrorEmbed(`Could not find lyrics for ${mGuild.queue[0].video.title}`)]})
    }
    

    lyrics = await searches[0].lyrics();
    if (lyrics.length > 2047) {
        lyrics = lyrics.substring(0, 2047)
    }

    embed = functions.getSuccessEmbed(`Lyrics for ${mGuild.queue[0].video.title}`, lyrics)
    return await interaction.followUp({embeds:[embed]})
}

async function command_queue(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})

    mGuild = guilds[interaction.guild.id]

    queue = `_ _ `
    history = `_ _ `
    counter = 0

    for (video of mGuild.queue) {
        counter += 1
        if (counter == mGuild.index+1) {queue += `**`}
        if (video.video.title) {
            queue += `${counter}. [${video.video.title}](https://youtube.com/watch?v=${video.video.id}) - Requested by: ${video.requestor.user.username}#${video.requestor.user.discriminator} - ${video.video.durationFormatted}\n`
        } else {
            queue += `${counter}. https://youtube.com/watch?v=${video.video.id} - Requested by: ${video.requestor.user.username}#${video.requestor.user.discriminator}\n`
        }
        
        if (counter == mGuild.index+1) {queue += `**`}
    }
    if (mGuild.history) {
        counter = 0
        for (video of mGuild.history) {
            counter += 1

            history += `${0-((mGuild.history.length - counter) +1 )}. [${video.video.title}](https://youtube.com/watch?v=${video.video.id}) - Requested by: ${video.requestor.user.username}#${video.requestor.user.discriminator} - ${video.video.durationFormatted}\n`
        }
    }
    

    embed = new discord.MessageEmbed()
        .setTitle(`Music queue for this server`)
        .addField(`History`, history)
        .addField(`Queue`, queue)
        .setColor(`#FF8700`)
    
    return await interaction.reply({embeds:[embed]})
}

async function command_volume(interaction) {
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})
    
    musicPermissions = await getMusicPermissions(interaction.guild.id)

    if (!musicPermissions.commands || !musicPermissions.commands.volume) {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    }


    mGuild = guilds[interaction.guild.id]

    mGuild.resource.volume.setVolume(interaction.options.getInteger("volume") /100)

    return interaction.reply({embeds:[functions.getSuccessEmbed(
        `Successfully set volume`, 
        `Successfully set volume of [${mGuild.queue[0].video.title}](https://youtube.com/watch?v=${mGuild.queue[0].video.id}) to **${interaction.options.getInteger("volume")}%**`
    )]})
}

async function command_pause(interaction) {
    mGuild = guilds[interaction.guild.id]
    
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})
    if (!mGuild.history) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NoBack)]})

    if (!musicPermissions.commands || !musicPermissions.commands.pause || musicPermissions.commands.pause == "permissions") {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    } else if (musicPermissions.commands.pause == "voting") {
        vote = await doVotes("pause", interaction.member, musicPermissions, interaction.memberPermissions, interaction.guild.id)

        if (!vote.do) {
            if (vote.voted) {
                return await interaction.reply({embeds:[functions.getEmbed(
                    `Voted to pause song (${vote.votes}/${vote.required})`, 
                    `Get more votes and the song will be paused (others have to do \`/pause\`)`)]}
                )
                
            } else {
                return await interaction.reply({embeds:[functions.getErrorEmbed(
                    `You have already voted to pause! (${vote.votes}/${vote.required})`)]}
                )
            }
        }
    }

    await mGuild.player.pause()
    mGuild.startedTime = ((new Date() - mGuild.startedAt) / 1000) + mGuild.startedTime
    

    return interaction.reply({embeds:[functions.getSuccessEmbed(
        `Successfully paused`, 
        `Successfully paused [${mGuild.queue[0].video.title}](https://youtube.com/watch?v=${mGuild.queue[0].video.id})`
    )]})
}

async function command_resume(interaction) {
    mGuild = guilds[interaction.guild.id]
    
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})
    if (!mGuild.history) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NoBack)]})

    if (!musicPermissions.commands || !musicPermissions.commands.resume || musicPermissions.commands.resume == "permissions") {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    } else if (musicPermissions.commands.resume == "voting") {
        vote = await doVotes("resume", interaction.member, musicPermissions, interaction.memberPermissions, interaction.guild.id)

        if (!vote.do) {
            if (vote.voted) {
                return await interaction.reply({embeds:[functions.getEmbed(
                    `Voted to resume song (${vote.votes}/${vote.required})`, 
                    `Get more votes and the song will be resumed (others have to do \`/resume\`)`)]}
                )
                
            } else {
                return await interaction.reply({embeds:[functions.getErrorEmbed(
                    `You have already voted to resume! (${vote.votes}/${vote.required})`)]}
                )
            }
        }
    }

    await mGuild.player.unpause()
    mGuild.startedAt = new Date()

    nowPlaying = await getNowPlaying(interaction.guild.id)

    return await interaction.reply({embeds:[nowPlaying.setColor("#00FF00")]})
}

async function command_seek(interaction) {

    mGuild = guilds[interaction.guild.id]
    
    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})
    
    musicPermissions = await getMusicPermissions(interaction.guild.id)

    if (!musicPermissions.commands || !musicPermissions.commands.seek) {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    }

    await interaction.deferReply()

    guilds[interaction.guild.id].queue[0].seek = interaction.options.getInteger("seek")
    await guilds[interaction.guild.id].playLoop()

    nowPlaying = await getNowPlaying(interaction.guild.id)

    return await interaction.followUp({embeds:[nowPlaying.setColor("#00FF00")]})
}

async function getNowPlaying(guildId, index=0) {
    mGuild = guilds[guildId]

    if (index == 0) {
        index = mGuild.index
    }

    embed = new discord.MessageEmbed()
        .setColor(`#FF8700`)
        .setTitle(`Now playing:`)
        .addField(`Requestor`, mGuild.queue[index].requestor.user.username + "#" + mGuild.queue[index].requestor.user.discriminator, inline=true)
    
    if (index > 0) {
        embed.setTitle(`Added to queue:`)
    }

    if (mGuild.queue[index].video.thumbnail) {
        embed.setThumbnail(mGuild.queue[index].video.thumbnail.url)
        embed.setDescription(`[${mGuild.queue[index].video.title}](https://youtube.com/watch?v=${mGuild.queue[index].video.id})`)

        if (index == 0) {
            multiplier = 1;if (mGuild.filters.speed) {multiplier = mGuild.filters.speed / 100}
            timeSince = (((new Date() - mGuild.startedAt) / 1000) + mGuild.startedTime) * multiplier
            var minutes = Math.floor(Math.round(timeSince) / 60);
            var seconds = Math.round(timeSince - minutes * 60)
            embed.addField(`Time`, `${minutes}:${seconds.toString().padStart(2, "0")} / ${mGuild.queue[index].video.durationFormatted}`, inline=true)

            timeBar = ``
            timeBarWidth = 20
            chunks = mGuild.queue[index].video.duration / timeBarWidth
            
            for(var i = 0; i < timeBarWidth; i++){
                if ((i+1) * chunks <= (timeSince*1000)) {
                    timeBar += `▓`
                } else {
                    timeBar += `░`
                }
                
                
            }
            embed.addField(`Progress`, timeBar)
        } else {
            embed.addField(`Time`, mGuild.queue[index].video.durationFormatted, inline=true)
        }

    } else {
        embed.setDescription(`Couldn't get detailed song information.\nhttps://youtube.com/watch?v=${mGuild.queue[index].video.id}`)
    }
        
    
    return embed
}

async function command_filter(interaction) {
    

    if (!interaction.member.voice.channelId) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotInVoiceChannel)]})
    if (!guilds[interaction.guild.id] || !guilds[interaction.guild.id].queue) return interaction.reply({embeds:[functions.getErrorEmbed(errors.NotPlaying)]})

    musicPermissions = await getMusicPermissions(interaction.guild.id)

    if (!musicPermissions.commands || !musicPermissions.commands.loop) {
        if (!interaction.memberPermissions.has(musicPermissions.permissions)) return interaction.reply({embeds:[functions.getErrorEmbed(errors.missingPermissions(musicPermissions.permissions))]})
    }

    if (interaction.options.getInteger("bass") != null) {
        if (interaction.options.getInteger("bass") != 100) {
            if (guilds[interaction.guild.id].filters.pitch && interaction.options.getInteger("pitch") != 0) {
                return await interaction.reply({embeds:[functions.getErrorEmbed(`You can't use bass and pitch filter at the same time! Use \`/filter bass:${interaction.options.getInteger("bass")} pitch:0\` to remove pitch filter and set bass.`)]})
            }
            if (guilds[interaction.guild.id].filters.speed && interaction.options.getInteger("speed") != 100) {
                return await interaction.reply({embeds:[functions.getErrorEmbed(`You can't use bass and speed filter at the same time! Use \`/filter bass:${interaction.options.getInteger("bass")} speed:100\` to remove pitch filter and set speed.`)]})
            }

            if (guilds[interaction.guild.id].filters.bass) {
                guilds[interaction.guild.id].filters.bass = interaction.options.getInteger("bass")
            } else {
                guilds[interaction.guild.id].filters.bass = interaction.options.getInteger("bass")
            }

        } else {
            if (guilds[interaction.guild.id].filters.bass) {
                delete guilds[interaction.guild.id].filters.bass
            }
            
        }
    }

    if (interaction.options.getInteger("pitch") != null) {
        if (interaction.options.getInteger("pitch") != 0) {
            if (guilds[interaction.guild.id].filters.bass && interaction.options.getInteger("bass") != 100) {
                return await interaction.reply({embeds:[functions.getErrorEmbed(`You can't use bass and pitch filter at the same time! Use \`/filter bass:100 pitch:${interaction.options.getInteger("pitch")}\` to remove bass filter and set pitch.`)]})
            }

            if (guilds[interaction.guild.id].filters.pitch) {
                guilds[interaction.guild.id].filters.pitch = interaction.options.getInteger("pitch")
            } else {
                guilds[interaction.guild.id].filters.pitch = interaction.options.getInteger("pitch")
            }

        } else {
            if (guilds[interaction.guild.id].filters.pitch) {
                delete guilds[interaction.guild.id].filters.pitch
            }
        }
    }

    if (interaction.options.getInteger("speed") != null) {
        if (interaction.options.getInteger("speed") != 100) {
            if (guilds[interaction.guild.id].filters.bass && interaction.options.getInteger("bass") != 100) {
                return await interaction.reply({embeds:[functions.getErrorEmbed(`You can't use bass and speed filter at the same time! Use \`/filter bass:100 speed:${interaction.options.getInteger("speed")}\` to remove bass filter and set speed.`)]})
            }

            if (guilds[interaction.guild.id].filters.speed) {
                guilds[interaction.guild.id].filters.speed = interaction.options.getInteger("speed")
            } else {
                guilds[interaction.guild.id].filters.speed = interaction.options.getInteger("speed")
            }

        } else {
            if (guilds[interaction.guild.id].filters.speed) {
                delete guilds[interaction.guild.id].filters.speed
            }
        }
    }

    multiplier = 1;if (guilds[interaction.guild.id].filters.speed) {multiplier = guilds[interaction.guild.id].filters.speed / 100}
    timeSince = (((new Date() - mGuild.startedAt) / 1000) + mGuild.startedTime) * multiplier
    guilds[interaction.guild.id].queue[0].seek = timeSince

    await guilds[interaction.guild.id].playLoop()

    guilds[interaction.guild.id].queue[0].seek = 0

    filtersStr = ``
    if (guilds[interaction.guild.id].filters.bass) filtersStr += `Bass: **${guilds[interaction.guild.id].filters.bass}%**`
    if (guilds[interaction.guild.id].filters.speed) filtersStr += `Speed: **${guilds[interaction.guild.id].filters.speed}%**`
    if (guilds[interaction.guild.id].filters.pitch) filtersStr += `Pitch: *${guilds[interaction.guild.id].filters.pitch}**`

    return interaction.reply({embeds:[functions.getSuccessEmbed("Set filters", `Successfully set filters:\n${filtersStr}`)]})
}

bot.login(process.env.token)