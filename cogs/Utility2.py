import discord, random, os, json
from discord.ext import commands
from functions import customerror, functions, google
from setup import var
from datetime import datetime, timedelta
from discordwebhook import asyncCreate
import aiohttp

class Utility2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="embed", description="[message]|Create an embed")
    async def embed(self, ctx, *, message = None):
        prefix = functions.prefix(ctx.guild)
        if message == None:
            embed = discord.Embed(title="Help for {}embed".format(prefix), color=var.embed)
            embed.add_field(name="Arguments", value= "{}embed [message]".format(prefix))
            embed.add_field(name="Options", value="""
`me=true` - Send as yourself (with a webhook)
`color=[hex color or simple color in a word]` - Set embed color
`title=[Title surrounded by [] or ()]` - Add a title to the embed 
`footer=[Footer for the embed surrounded by [] or ()]` - Add a footer to the embed
`image=[image url]` - Add an image to the embed
            """, inline=False)
            await ctx.send(embed=embed)
        else:
            done = 0
            title = False
            footer = False
            image = False
            for item in message.split(" "):
                if "color=" in item or "colour=" in item:
                    color_orig = item.replace("color=", "").replace("colour=", "")
                    color = color_orig.replace("#", "")
                    if color.lower() in functions.colorfromword("getthem"):
                        col = functions.colorfromword(color)
                        me_col = functions.colorfromword(color)
                    else:
                        try:
                            col = discord.Color(value=int(color, 16))
                            me_col = int(color, 16)
                        except:
                            col = var.embed
                            me_col = var.embed
                    message = message.replace(f"color={color_orig}", "").replace(f"colour={color_orig}", "")
                    done = 1
                if "image=" in item:
                    image_url = item.replace("<", "").replace(">", "").replace("image=", "")
                    message = message.replace("<", "").replace(">", "").replace(f"image={image_url}", "")
                    image = True
                if "title=" in item:
                    if "[" in message and "]" in message.split("title=")[1]:
                        title_result = message[message.find("[")+1:message.find("]")]
                        message = message.replace("title=[{}]".format(title_result), "")
                    elif "(" in message and ")" in message.split("title=")[1]:
                        title_result = message[message.find("(")+1:message.find(")")]
                        message = message.replace("title=({})".format(title_result), "")
                    else:
                        return await ctx.send(f"{ctx.message.author.mention} please input a title surrounded by `()` or `[]`")
                    title = True
                if "footer=" in item:
                    if "[" in message and "]" in message.split("footer=")[1]:
                        footer_result = message[message.find("[")+1:message.find("]")]
                        message = message.replace("footer=[{}]".format(footer_result), "")
                    elif "(" in message and ")" in message.split("footer=")[1]:
                        footer_result = message[message.find("(")+1:message.find(")")]
                        message = message.replace("footer=({})".format(footer_result), "")
                    else:
                        return await ctx.send(f"{ctx.message.author.mention} please input a footer surrounded by `()` or `[]`")
                    footer = True
            if done != 1:
                col = var.embed
                me_col = var.embed
            if "webhook=true" in message or "me=true" in message:
                message = message.replace("webhook=true", "").replace("me=true", "")
                try:
                    await ctx.message.delete()
                except:
                    pass

                try:
                    webhooks = await ctx.message.channel.webhooks()

                    if len(webhooks) == 0:
                        finalwebhook = await ctx.message.channel.create_webhook(name="Helper Webhook")
                    else:
                        finalwebhook = webhooks[0]
                except:
                    raise commands.BotMissingPermissions(["manage_webhooks"])
                
                main = asyncCreate.Webhook()
                main.avatar_url(str(ctx.message.author.avatar_url))
                main.author(ctx.message.author.display_name)

                embed = asyncCreate.Embed()
                if title == True:
                    embed.title(title_result)
                if footer == True:
                    embed.set_footer(text=footer_result)
                if image == True:
                    embed.set_thumbnail(url=image_url)
                embed.description(message)
                embed.color(me_col) 

                return await main.send(finalwebhook.url, embed=embed)
            try:
                await ctx.message.delete()
            except:
                pass
            
            if title == True:
                embed = discord.Embed(title=title_result, description=message, color=col)
            else:
                embed = discord.Embed(description=message, color=col)
            if footer == True:
                embed.set_footer(text=footer_result)
            if image == True:
                embed.set_thumbnail(url=image_url)
            await ctx.send(embed=embed)

    @commands.command(name='question', description="[question] | [ans1] / [ans2] / *[ans3] / *[ans4] / *[ans5] etc... (max 10)|Create a multiple choice question")
    async def question(self, ctx, *, input = None):
        prefix = functions.prefix(ctx.guild)
        try:
            await ctx.message.delete()
        except:
            pass

        failEmbed = discord.Embed(title="Help for {}question".format(prefix), color=var.embed)
        failEmbed.add_field(name="What it does", value= "{}question - Create a multiple choice question".format(prefix), inline = False)
        failEmbed.add_field(name="Arguments", value= f"{prefix}question Question | Answer1 / Answer2 / Answer3 (Optional) / Answer4 (Optional) / Answer5 (Optional) etc... (max 10)", inline = False)
        failEmbed.add_field(name="Example", value= "{}question How are you? | Good / Bad/ Meh / Awful".format(prefix), inline = False)

        if input == None:
            
            await ctx.send(embed=failEmbed)
        else:
            if "|" not in input or "/" not in input:
                await ctx.send(embed=failEmbed)
            else:
                inputs = input.split('|')
                a = inputs[1].split('/')
                question = inputs[0]
                emb = discord.Embed(title="Question from {}".format(ctx.message.author), description=question, colour=var.embed)
                o1,o2,o3,o4,o5,o6,o7,o8,o9,o10 = (None, None, None, None, None, None, None, None, None, None)
                try:
                    emb.add_field(name="Option 1", value=a[0])
                    o1 = "Got it"
                except:
                    pass
                try:
                    emb.add_field(name="Option 2", value=a[1])
                    o2 = "Got it"
                except:
                    pass
                try:
                    emb.add_field(name="Option 3", value=a[2])
                    o3 = "Got it"
                except:
                    pass
                try:
                    emb.add_field(name="Option 4", value=a[3])
                    o4 = "Got it"
                except:
                    pass
                try:
                    emb.add_field(name="Option 5", value=a[4])
                    o5 = "Got it"
                except:
                    pass
                try:
                    emb.add_field(name="Option 6", value=a[5])
                    o6 = "Got it"
                except:
                    pass
                try:
                    emb.add_field(name="Option 7", value=a[6])
                    o7 = "Got it"
                except:
                    pass
                try:
                    emb.add_field(name="Option 8", value=a[7])
                    o8 = "Got it"
                except:
                    pass
                try:
                    emb.add_field(name="Option 9", value=a[8])
                    o9 = "Got it"
                except:
                    pass
                try:
                    emb.add_field(name="Option 10", value=a[9])
                    o10 = "Got it"
                except:
                    pass
                re = await ctx.send(embed=emb)
                if o1 != None:
                    await re.add_reaction("1️⃣")
                if o2 != None:
                    await re.add_reaction("2️⃣")
                if o3 != None:
                    await re.add_reaction("3️⃣")
                if o4 != None:
                    await re.add_reaction("4️⃣")
                if o5 != None:
                    await re.add_reaction("5️⃣")
                if o6 != None:
                    await re.add_reaction("6️⃣")
                if o7 != None:
                    await re.add_reaction("7️⃣")
                if o8 != None:
                    await re.add_reaction("8️⃣")
                if o9 != None:
                    await re.add_reaction("9️⃣")
                if o10 != None:
                    await re.add_reaction("🔟")
    
    @commands.command(name="covid", description="*[country]|Get coronavirus statistics for a country", aliases=['coronacount', "corona", "covid-19", "covid19count", "covidcount", "coronavirus"])
    async def covid(self, ctx, *, country = None):
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
                            except:
                                pass
                    
                    if done == False:
                        embed = discord.Embed(title="Available countries", 
                            description=", ".join([item for item in names]),
                            color=var.embed)
                        return await ctx.send(embed=embed)

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
                    return await ctx.send(embed=embed)
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
                    return await ctx.send(embed=embed)
        
def setup(bot):
    bot.add_cog(Utility2(bot))