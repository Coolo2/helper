const discord = require("discord.js-light")



module.exports.getErrorEmbed = function (description) {
        embed = new discord.MessageEmbed()
                .setColor("#FF0000")
                .setDescription(description)
                .setTitle("Oops!")
    
        return embed
}

module.exports.getSuccessEmbed = function (title, description) {
        embed = new discord.MessageEmbed()
                .setColor("#00FF00")
                .setDescription(description)
                .setTitle(title)
    
        return embed
}

module.exports.getEmbed = function (title, description) {
        embed = new discord.MessageEmbed()
                .setColor("#FF8700")
                .setDescription(description)
                .setTitle(title)
    
        return embed
}

module.exports.Errors = class {
        constructor() {
                this.NotInVoiceChannel = "You are not in a voice channel!"
                this.NotPlaying = "I'm not currently playing anything!"
                this.NoBack = "There is nothing to go back to!"
                this.NoSongFound = "No song was found for that query... Maybe try a URL?"
                this.VoicePermissions = "I do not have permission to join this voice channel. Make sure I have correct permissions to use music commands!"
                this.InvalidTrack = "Could not find valid track/index... Maybe try use the options provided?"
                this.MissingPermissions = "You are missing `move_members` permissions to run this command."

                this.missingPermissions = function (permission) {
                    return `You are missing \`${permission}\` permissions to run this command.`
                }
        }

    
}