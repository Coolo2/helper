from discord.ext import commands 
import discord

from functions import functions
from setup import var
from datetime import datetime
import helper

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
        description : str = None,
        me : bool = None,
        title : str = None,
        footer : str = None,
        color : str = None,
        image : str = None
    ):
        
        if description == None and title == None and footer == None and image == None:
            raise helper.errors.MildErr("You must provide some text/imagery!")

        start_time = datetime.now()

        embed = discord.Embed() 

        if color == None:
            color = "None"

        color = color.replace("#", "")
        colorfromword = functions.colorfromword(color)
        if colorfromword:
            embed.color = colorfromword
        else:
            try:
                embed.color = int(color, 16)
            except Exception as e:
                pass

        if title:
            embed.title = title
        if footer:
            embed.set_footer(text=footer)
        if description:
            embed.description = description
        if image:
            embed.set_thumbnail(url=image)

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
            

            
            await webhook.send(embed=embed, username=ctx.user.display_name, avatar_url=ctx.user.display_avatar.url if ctx.user.display_avatar else None, wait=False)

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

        await ctx.response.send_message(embed=embed)

        re = await ctx.original_response()
        
        for i in range(len(choices)):
            await re.add_reaction(emojis[i])
        
async def setup(bot):
    await bot.add_cog(Utility2(bot))