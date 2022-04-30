from enum import auto
from discord.ext import commands 
import discord

import asyncio
import datetime
from setup import var

# Code is in discord.js, Music dir
# Registering commands

from discord import app_commands

async def autocomplete_blank(ctx, current):
    pass

class Music(commands.Cog):
    def __init__(self, bot : discord.Client):
        self.bot = bot
    
    async def noResponse(self, ctx : discord.Interaction):
        await asyncio.sleep(2.5)
        try:
            await ctx.response.send_message(
                embed=discord.Embed(title="Oops!", 
                    description=f"Music command didn't respond. Either it is offline or an unexpected error occurred.\n\nJoin the [Support Server]({var.server}) for support.", 
                    color=var.embedFail, timestamp=datetime.datetime.now()))
            return await self.bot.get_channel(927926604838109215).send(f"> Error in **{ctx.guild.name}** from **{ctx.user}**: `Music section offline / error`")
        except Exception as e:
            pass

    @app_commands.command(name="play", description="Play a song from a YouTube URL or search")
    @app_commands.autocomplete(song=autocomplete_blank)
    @app_commands.describe(song="The song URL or name to play", seek="A timestamp to seek to")
    async def play(
            self, 
            ctx, 
            song : str, 
            seek : app_commands.Range[int, 1] = None
    ):
        await self.noResponse(ctx)

    @app_commands.command(name="stop", description="Stop player")
    async def stop(self, ctx):
        await self.noResponse(ctx)

    @app_commands.command(name="skip", description="Skip to next song or end")
    async def skip(self, ctx):
        await self.noResponse(ctx)

    @app_commands.command(name="now-playing", description="Get the currently playing song")
    async def nowplaying(self, ctx):
        await self.noResponse(ctx)

    @app_commands.command(name="queue", description="Get the song queue and history")
    async def queue(self, ctx):
        await self.noResponse(ctx)

    @app_commands.command(name="back", description="Go back a song")
    async def back(self, ctx):
        await self.noResponse(ctx)

    @app_commands.command(name="volume", description="Set the audio volume")
    @app_commands.describe(volume="The volume (0-10,000%) to set to")
    async def volume(self, ctx, volume : app_commands.Range[int, 0, 10000]):
        await self.noResponse(ctx)

    @app_commands.command(name="pause", description="Pause the currently playing track")
    async def pause(self, ctx):
        await self.noResponse(ctx)

    @app_commands.command(name="resume", description="Resume playing the paused track")
    async def resume(self, ctx):
        await self.noResponse(ctx)
    
    @app_commands.command(name="seek", description="Seek to a time in the currently playing track")
    @app_commands.describe(seek="The time in seconds to seek to")
    async def seek(self, ctx, seek : app_commands.Range[int, 0]):
        await self.noResponse(ctx)
    
    @app_commands.command(name="lyrics", description="Get lyrics for currently playing track")
    async def lyrics(self, ctx):
        await self.noResponse(ctx)
    
    @app_commands.command(name="restart", description="Restart to beginning of currently playing track")
    async def restart(self, ctx):
        await self.noResponse(ctx)
    
    @app_commands.command(name="skipto", description="Skip to a certain track")
    @app_commands.describe(track="The track to skip to")
    @app_commands.autocomplete(track=autocomplete_blank)
    async def skipto(self, ctx, track: str):
        await self.noResponse(ctx)
    
    @app_commands.command(name="remove", description="Remove track from queue")
    @app_commands.describe(track="The track to remove")
    @app_commands.autocomplete(track=autocomplete_blank)
    async def remove(self, ctx, track: str):
        await self.noResponse(ctx)
    
    @app_commands.command(name="loop", description="Loop track or whole queue")
    @app_commands.describe(type="The type of loop (queue or track or none)")
    @app_commands.choices(type=[app_commands.Choice(name="Queue", value="queue"), app_commands.Choice(name="Track", value="track"), app_commands.Choice(name="Off", value="off")])
    async def loop(self, ctx, type: str):
        await self.noResponse(ctx)
    
    @app_commands.command(name="filter", description="Add effects and filters to the player")
    @app_commands.describe(pitch="Default 0. Integer from -12 to +12 as the pitch in semitones.", bass="Default 100%. % of original bass. Any number from 50-10000%", speed="Default 100%. % of original bass. Any number from 50-500%")
    async def filter(
        self, 
        ctx : discord.Interaction,
        pitch : app_commands.Range[int, -12, 12],
        bass : app_commands.Range[int, 50, 10_000],
        speed : app_commands.Range[int, 50, 500]
    ):
        await self.noResponse(ctx)




async def setup(bot):
    await bot.add_cog(Music(bot), guilds=var.guilds)