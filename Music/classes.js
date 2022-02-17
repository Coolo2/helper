const discord = require("discord.js-light")

module.exports.musicGuild = class {
    constructor(bot, guild) {
        this.bot = bot 
        this.guild = guild
    }
}