from discord.ext import commands 
import discord

from discord.commands import slash_command, Option

import asyncio
import datetime
from setup import var

from functions import library_overwrites

# Code is in discord.js, Music dir
# Registering commands

discord.SlashCommandGroup.invoke_autocomplete_callback = library_overwrites.invoke_autocomplete_callback

async def autocomplete_blank(ctx):
    pass

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def noResponse(self, ctx):
        await asyncio.sleep(2.5)
        try:
            await ctx.respond(
                embed=discord.Embed(title="Oops!", 
                    description=f"Music command didn't respond. Either it is offline or an unexpected error occurred.\n\nJoin the [Support Server]({var.server}) for support.", 
                    color=var.embedFail, timestamp=datetime.datetime.now()))
            return await self.bot.get_channel(927926604838109215).send(f"> Error in **{ctx.guild.name}** from **{ctx.author}**: `Music section offline / error`")
        except:
            pass

    @slash_command(name="play", description="Play a song from a YouTube URL or search")
    async def play(
        self, 
        ctx, 
        song : Option(str, description="The song URL or name to play", autocomplete=autocomplete_blank), 
        seek : Option(int, description="The timestamp to seek to", required=False, min_value=1)):
        await self.noResponse(ctx)

    @slash_command(name="stop", description="Stop player")
    async def stop(self, ctx):
        await self.noResponse(ctx)

    @slash_command(name="skip", description="Skip to next song or end")
    async def skip(self, ctx):
        await self.noResponse(ctx)

    @slash_command(name="now-playing", description="Get the currently playing song")
    async def nowplaying(self, ctx):
        await self.noResponse(ctx)

    @slash_command(name="queue", description="Get the song queue and history")
    async def queue(self, ctx):
        await self.noResponse(ctx)

    @slash_command(name="back", description="Go back a song")
    async def back(self, ctx):
        await self.noResponse(ctx)

    @slash_command(name="volume", description="Set the audio volume")
    async def volume(self, ctx, volume : Option(int, description="The volume (0-1000%) to set to.", min_value=0, max_value=1000)):
        await self.noResponse(ctx)

    @slash_command(name="pause", description="Pause the currently playing track")
    async def pause(self, ctx):
        await self.noResponse(ctx)

    @slash_command(name="resume", description="Resume playing the paused track")
    async def resume(self, ctx):
        await self.noResponse(ctx)
    
    @slash_command(name="seek", description="Seek to a time in the currently playing track")
    async def seek(self, ctx, seek : Option(int, description="The time in seconds to seek to", min_value=0)):
        await self.noResponse(ctx)
    
    @slash_command(name="lyrics", description="Get lyrics for currently playing track")
    async def lyrics(self, ctx):
        await self.noResponse(ctx)
    
    @slash_command(name="restart", description="Restart to beginning of currently playing track")
    async def restart(self, ctx):
        await self.noResponse(ctx)
    
    @slash_command(name="skipto", description="Skip to a certain track")
    async def skipto(self, ctx, track: Option(str, description="The track to skip to", autocomplete=autocomplete_blank)):
        await self.noResponse(ctx)
    
    @slash_command(name="remove", description="Remove track from queue")
    async def remove(self, ctx, track: Option(str, description="The track to remove", autocomplete=autocomplete_blank)):
        await self.noResponse(ctx)
    
    @slash_command(name="loop", description="Loop track or whole queue")
    async def loop(self, ctx, type: Option(str, description="The type of loop (queue or track or none)", choices=["queue", "track", "off"])):
        await self.noResponse(ctx)
    
    @slash_command(name="filter", description="Add effects and filters to the player")
    async def filter(
        self, 
        ctx,
        pitch : Option(int, description="Default 0. Integer from -12 to +12 as the pitch in semitones.", required=False, min_value=-12, max_value=12),
        bass : Option(int, description="Default 100%. % of original bass. Any number from 50-10000%", required=False, min_value=50, max_value=10_000),
        speed : Option(int, description="Default 100%. % of original speed. Any number from 50-1000%", required=False, min_value=50, max_value=500)
    ):
        await self.noResponse(ctx)




def setup(bot):
    bot.add_cog(Music(bot))