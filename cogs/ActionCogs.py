import discord
import random
from discord import app_commands
from discord.ext import commands
import gifs
from helpful_functions import random_color
# import hug_data
# import json

class actionCommandsCogs(commands.Cog):
    '''Contains action commands for the bot'''
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="hug", description="Hugs a user or maybe yourself as well?")
    async def hug(self, interaction : discord.Interaction, user : discord.Member = None):
        hug_description = ["Aww, that's so wholesome!", "That's nice!", "I'm so jealous!", "You never know how much a simple hug might mean to someone~", "After all, everyone deserves a hug, don't they?"]

        id = str(interaction.user.id)

        embed = discord.Embed(
            description=random.choice(hug_description),
            color=int(random_color(), 16)
        )
        embed.set_image(url=random.choice(gifs.action_gifs['hug_gifs']))

        if user == None or user == interaction.user:
            embed.title = f"{interaction.user.name}, lemme give you a hug! Such a precious little kiddo!"
        else:
            embed.title = f"{interaction.user.name} hugged {user.name} tightly! How adorable!"
        
        await interaction.response.send_message(embed=embed)


async def setup(client: commands.Bot) -> None:
    await client.add_cog(actionCommandsCogs(client))