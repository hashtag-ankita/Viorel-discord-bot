import discord
from discord.ext import commands
from discord import app_commands
from dotenv import *
from os import *
from sys import *
import asyncio
from json import *

load_dotenv()

class ownerCommandsCogs(commands.Cog):
    '''Contains special commands for the bot (can be run by owner only)'''
    def __init__(self, client: commands.Bot):
        self.client = client
        self.client.target_channel = None

    @app_commands.command(name="shutdown", description="Shuts down the bot")
    @commands.check(lambda i: i.user.id == int(getenv("OWNER_ID")))
    async def shutdown(self, interaction: discord.Interaction):
        if interaction.user.id != int(getenv("OWNER_ID")):
            await interaction.response.send_message("You don't have the permission to use this command!", ephemeral=True)
            return
        await interaction.response.send_message("Shutting down...")
        await self.client.close()

    @app_commands.command(name="restart", description="Restarts the bot")
    @commands.check(lambda i: i.user.id == int(getenv("OWNER_ID")))
    async def restart(self, interaction: discord.Interaction):
        if interaction.user.id != int(getenv("OWNER_ID")):
            await interaction.response.send_message("You don't have the permission to use this command!", ephemeral=True)
            return
        await interaction.response.send_message("Restarting...")
        execv(executable, ['python'] + argv)

    @app_commands.command(name="reload_cog", description="Reloads a cog")
    @commands.check(lambda i: i.user.id == int(getenv("OWNER_ID")))
    async def reload_cog(self, interaction: discord.Interaction, cog: str):
        if interaction.user.id != int(getenv("OWNER_ID")):
            await interaction.response.send_message("You don't have the permission to use this command!", ephemeral=True)
            return

        try:
            self.client.unload_extension(f"cogs.{cog}")
            self.client.load_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"```Cog {cog} reloaded successfully.```")
        except Exception as e:
            await interaction.response.send_message(f"```Error: {e}```")

    @app_commands.command(name="unload_cog", description="Unloads a cog")
    @commands.check(lambda i: i.user.id == int(getenv("OWNER_ID")))
    async def unload_cog(self, interaction: discord.Interaction, cog: str):
        if interaction.user.id != int(getenv("OWNER_ID")):
            await interaction.response.send_message("You don't have the permission to use this command!", ephemeral=True)
            return

        try:
            self.client.unload_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"```Cog {cog} unloaded successfully.```")
        except Exception as e:
            await interaction.response.send_message(f"```Error: {e}```")


    @app_commands.command(name="load_cog", description="loads a cog")
    @commands.check(lambda i: i.user.id == int(getenv("OWNER_ID")))
    async def load_cog(self, interaction: discord.Interaction, cog: str):
        if interaction.user.id != int(getenv("OWNER_ID")):
            await interaction.response.send_message("You don't have the permission to use this command!", ephemeral=True)
            return

        try:
            self.client.load_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"```Cog {cog} loaded successfully.```")
        except Exception as e:
            await interaction.response.send_message(f"```Error: {e}```")

    
    @app_commands.command(name="set_target_channel", description="Sets the target channel for relay message")
    @commands.check(lambda i: i.user.id == int(getenv("OWNER_ID")))
    #channel can be discord.textchannel or channel_id
    async def set_target_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.user.id != int(getenv("OWNER_ID")):
            await interaction.response.send_message("You don't have the permission to use this command!", ephemeral=True)
            return
        self.client.target_channel = channel
        await interaction.response.send_message(f"Target channel set to **{channel.mention}**")


    @app_commands.command(name="set_target_channel_id", description="Target channel for relay message")
    @commands.check(lambda i: i.user.id == int(getenv("OWNER_ID")))
    async def set_target_channel_id(self, interaction: discord.Interaction, channel_id: str):
        '''to be used if channel is being set from different server'''
        if interaction.user.id != int(getenv("OWNER_ID")):
            await interaction.response.send_message("You don't have the permission to use this command!", ephemeral=True)
            return
        self.client.target_channel = int(channel_id)
        await interaction.response.send_message(f"Target channel set to <#{channel_id}>")


    #a function to relay message to my development server in discord
    async def relay_message(self, message: str):
        if self.client.target_channel is None:
            return "Target channel is not set."
        
        target_channel = self.client.target_channel

        if isinstance(target_channel, int):
            target_channel = self.client.get_channel(target_channel)

        if target_channel is None:
            return "Target channel not found."

        if isinstance(message, discord.Embed):
            await target_channel.send(embed=message)
        else:
            await target_channel.send(message)

    @app_commands.command(name="make_note", description="Makes a note for owner")
    @commands.check(lambda i: i.user.id == int(getenv("OWNER_ID")))
    async def make_note(self, interaction: discord.Interaction, message: str):
        if interaction.user.id != int(getenv("OWNER_ID")):
            await interaction.response.send_message("You don't have the permission to use this command!", ephemeral=True)
            return

        embed = discord.Embed(title="Personal Note", description=message, color=discord.Color.dark_purple())
        embed.set_footer(text="Note created by " + interaction.user.name)

        await self.relay_message(embed)
        await interaction.response.send_message(f"Personal note added to my server!")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ownerCommandsCogs(client))