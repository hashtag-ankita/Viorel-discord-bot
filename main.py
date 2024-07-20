import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import time
import os
import dotenv
import typing


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('v!'), intents=discord.Intents().all())

        self.cogsList = ["cogs.ActionCogs", "cogs.ModerationCogs", "cogs.OwnerOnlyCogs", "cogs.LanguageCogs"]

    async def setup_hook(self):
        for ext in self.cogsList:
            await self.load_extension(ext)

    async def on_ready(self):
        await self.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.listening, name="my Ann~"))
        print(f"Logged in as {self.user.name}")
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands.")
        except Exception as e:
            print(e)
        print("------------------------------------------------")

    @app_commands.command(name="help", description="help command")
    async def help_command(self, interaction: discord.Interaction, category: typing.Literal["Action", "Moderation", "OwnerOnly", "Language"] = None):
        if category:
            if category == "Action":
                embed = discord.Embed(title="Action Commands", description="Here are all the action commands for the bot.")
            elif category == "Moderation":
                embed = discord.Embed(title="Moderation Commands", description="Here are all the moderation commands for the bot.")
            elif category == "OwnerOnly":
                embed = discord.Embed(title="Owner Only Commands", description="Here are all the owner only commands for the bot.")

            for command in self.tree.walk_commands():
                if command.parent and command.parent.name == category:
                    embed.add_field(name=f"/{command.name}", value=command.description, inline=False)

            await interaction.response.send_message(embed=embed)

dotenv.load_dotenv()

client = Client()
client.run(os.getenv("BOT_TOKEN"))
