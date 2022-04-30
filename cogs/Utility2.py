from discord.ext import commands 
import discord

import random, os, json
from discord import webhook
from functions import customerror, functions, google
from setup import var
from datetime import datetime, timedelta
import aiohttp

from discord import app_commands

class Utility2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="embed", description="Create an embed")
    @app_commands.describe(
        description="The description to go in the embed",
        me="Whether the embed is sent as yourself",
        title="The title of the embed",
        footer="The footer of the embed",
        color="The color of the embed (hex or text)",
        image="An image URL for the embed"
    )
    async def embed(
        self, 
        ctx : discord.Interaction, 
        description : str,
        me : bool = None,
        title : str = None,
        footer : str = None,
        color : str = None,
        image : str = None
    ):
        start_time = datetime.now()

        embed = None 
        webhookEmbed = None

        if color == None:
            color = "None"

        color = color.replace("#", "")
        if color.lower() in functions.colorfromword("getthem"):
            color = functions.colorfromword(color)
        else:
            try:
                color = int(color, 16)
            except Exception as e:
                color = var.embed

        if title and footer:
            embed = discord.Embed(title=title, description=description, color=color)
        elif title:
            embed = discord.Embed(title=title, description=description)
        else:
            embed = discord.Embed(description=description)
        
        if footer:
            embed.set_footer(text=footer)
            webhookEmbed.set_footer(text=footer)
        if image:
            embed.set_thumbnail(url=image)
            webhookEmbed.set_thumbnail(url=image)

        if me:

            try:
                webhooks = await ctx.channel.webhooks()

                if len(webhooks) == 0:
                    webhook = await ctx.channel.create_webhook(name="Helper Webhook")
                else:
                    webhook = webhooks[0]
            except Exception as e:
                print(e)
                raise commands.BotMissingPermissions(["manage_webhooks"])
            

            
            await webhook.send(embed=embed, username=ctx.user.display_name, avatar_url=ctx.user.avatar.url if ctx.user.avatar else None, wait=False)

            timeElapsed = round((datetime.now() - start_time).total_seconds(), 3)

            return await ctx.response.send_message(f"Complete `{timeElapsed}s`", ephemeral=True)
        
        await ctx.response.send_message(embed=embed)

        

    @app_commands.command(name='question', description="Create a multiple choice question")
    @app_commands.describe(
        question="The question to provide choices for",
        choice1="The 1st choice",
        choice2="The 2nd choice",
        choice3="The 3rd choice",
        choice4="The 4th choice",
        choice5="The 5th choice",
        choice6="The 6th choice",
        choice7="The 7th choice",
        choice8="The 8th choice",
        choice9="The 9th choice",
        choice10="The 10th choice"
    )
    async def question(
        self, 
        ctx : discord.Interaction,
        question : str,
        choice1 : str,
        choice2 : str,
        choice3 : str = None,
        choice4 : str = None,
        choice5 : str = None,
        choice6 : str = None,
        choice7 : str = None,
        choice8 : str = None,
        choice9 : str = None,
        choice10 : str = None
    ):
        prefix = functions.prefix(ctx.guild)
        
        choices = [choice1, choice2, choice3, choice4, choice5, choice6, choice7, choice8, choice9, choice10]
        emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        choices = [x for x in choices if x is not None]

        embed = discord.Embed(title="Question from {}".format(ctx.user), description=question, colour=var.embed)

        index = 0
        for choice in choices:
            index += 1
            try:
                embed.add_field(name=f"Option {index}", value=choice)
            except Exception as e:
                pass

                
        org = await ctx.response.send_message(embed=embed)

        re = await ctx.original_message()
        
        for i in range(len(choices)):
            await re.add_reaction(emojis[i])
    
    @app_commands.command(name="covid", description="Get coronavirus statistics for a country")
    @app_commands.describe(country="Country to get stats for")
    async def covid(self, ctx : discord.Interaction, country : str = None):
        if (country != None):
            async with aiohttp.ClientSession() as session:
                async with session.get("http://country.io/names.json") as r:
                    names = await r.json()
                    reverse = {}
                    for item in names:
                        reverse[names[item].lower()] = item.lower()
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.apify.com/v2/key-value-stores/SmuuI0oebnTWjRTUh/records/LATEST?disableRedirect=true") as r:
                    rs = await r.json()
                    done = False
                    for country2 in rs["regionData"]:
                        if country2["country"].lower() == country.lower():
                            done = True
                            final = country2
                        else:
                            try:
                                if reverse[country2["country"].lower()] == country.lower():
                                    final = country2
                                    done = True
                            except Exception as e:
                                pass
                    
                    if done == False:
                        embed = discord.Embed(title="Available countries", 
                            description=", ".join([item for item in names]),
                            color=var.embed)
                        return await ctx.response.send_message(embed=embed)

                    embed = discord.Embed(title="Summary", 
                        description="Coronavirus summary for " + final["country"],
                        color=var.embed)
                    if final['country'].lower() in reverse:
                        embed.set_thumbnail(url=f"https://www.countryflags.io/{reverse[final['country'].lower()]}/flat/64.png")
                    embed.add_field(name='Total cases', value=format(final["totalCases"], ',d'))
                    embed.add_field(name='New daily cases', value=str(final["newCases"]).replace("0", "No data currently") if str(final["newCases"]) == "0" else format(final["newCases"], ',d'))
                    embed.add_field(name='Total deaths', value=format(final["totalDeaths"], ',d'))
                    embed.add_field(name='New daily deaths', value=str(final["newDeaths"]).replace("0", "No data currently") if str(final["newDeaths"]) == "0" else format(final["newDeaths"], ',d'))
                    embed.add_field(name='Total recovered', value=str(final["totalRecovered"]).replace("None", "No data") if str(final["totalRecovered"]) == "None" else format(final["totalRecovered"], ',d'))
                    embed.add_field(name='Active cases', value=str(final["activeCases"]).replace("None", "No data") if str(final["activeCases"]) == "None" else format(final["activeCases"], ',d'))
                    return await ctx.response.send_message(embed=embed)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.apify.com/v2/key-value-stores/SmuuI0oebnTWjRTUh/records/LATEST?disableRedirect=true") as r:
                    rs = await r.json()
                    embed = discord.Embed(title="Global summary", 
                        description="A summary of all global statistics",
                        color=var.embed)
                    embed.add_field(name='Total cases', value=format(rs["regionData"][0]["totalCases"], ',d'))
                    embed.add_field(name='New daily cases', value=format(rs["regionData"][0]["newCases"], ',d'))
                    embed.add_field(name='Total deaths', value=format(rs["regionData"][0]["totalDeaths"], ',d'))
                    embed.add_field(name='New daily deaths', value=format(rs["regionData"][0]["newDeaths"], ',d'))
                    embed.add_field(name='Total recovered', value=format(rs["regionData"][0]["totalRecovered"], ',d'))
                    embed.add_field(name='New daily recovered', value=format(rs["regionData"][0]["activeCases"], ',d'))
                    return await ctx.response.send_message(embed=embed)
        
async def setup(bot):
    await bot.add_cog(Utility2(bot), guilds=var.guilds)