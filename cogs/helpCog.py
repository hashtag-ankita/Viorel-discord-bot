from discord import *
from discord.ext import commands

class helpCog(commands.Cog):
    '''Contains help commands for the bot'''
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="help", description="Shows all available commands")
    async def help(self, interaction: Interaction):
        pass


async def setup(client: commands.Bot) -> None:
    await client.add_cog(helpCog(client))