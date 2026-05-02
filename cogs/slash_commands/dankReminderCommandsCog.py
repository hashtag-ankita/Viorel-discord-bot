'''
This is merely something I made for my own help in counting my dank memer badge progress and giving me reminders depending on what command it is. I have no plans to merge it with the main and might simply stay as an abandoned branch, for personal consultation later about stuff.
'''
import asyncio
import discord
from discord import app_commands
from discord.ext import commands, tasks
import time
import os
import dotenv
import json


class DankReminderCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = "dank_progress.json"
        self.counts = self.load_data()
        self.goals = {
            "giveaway": 1000,
            "hl": 12500,
            "pm": 2000,
            "beg": 10000,
            "tidy": 5000
        }

    def load_data(self):
        if not os.path.exists(self.file):
            return {}
        
        try:
            with open(self.file, "r") as f:
                return json.load(f)
            
        except:
            return {}
        

    def save_data(self):
        temp_file = self.file + ".tmp"

        with open(temp_file, "w") as f:
            json.dump(self.counts, f, indent=4)

        os.replace(temp_file, self.file)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if message.author.id != 837012323184148570:
            return
        
        content = message.content.lower()

        COMMAND_MAP = {
            "pls giveaway": "giveaway",
            "pass hl": "hl",
            "pass pm": "pm",
            "pass beg": "beg",
            "pass tidy": "tidy"
        }

        COMMAND_FAIL_MAP = {
            "fail giveaway": "giveaway",
            "fail hl": "hl",
            "fail pm": "pm",
            "fail beg": "beg",
            "fail tidy": "tidy"
        }

        for trigger, name in COMMAND_MAP.items():
            if content.startswith(trigger):
                await self.increment_count(message, name)

        for trigger, name in COMMAND_FAIL_MAP.items():
            if content.startswith(trigger):
                await self.decrement_count(message, name)

        # if content.startswith("pls giveaway create items"):
        #     await self.handle_giveaway(message)

        # elif content.startswith("pls hl"):
        #     await self.handle_hl(message)


    async def increment_count(self, message, command_name):
        user_id = str(message.author.id)

        if user_id not in self.counts:
            self.counts[user_id] = {}

        self.counts[user_id][command_name] = self.counts[user_id].get(command_name, 0) + 1
        self.save_data()

        embed = discord.Embed(
            title=f"{command_name.capitalize()} Count Updated",
            description=f"Current count for {command_name}: {self.counts[user_id][command_name]}/{self.goals[command_name]}",
            color=discord.Color.blue()
        )
        # embed.set_footer(text="If this was a mistake, use `fail {command_name}` to decrement the count. Thank you!")
        await message.channel.send(embed=embed)

        # optional cooldown tracking
        if command_name == "giveaway":
            asyncio.create_task(self.giveaway_reminder(message))


    async def decrement_count(self, message, command_name):
        user_id = str(message.author.id)

        if user_id not in self.counts or command_name not in self.counts[user_id]:
            return
        
        self.counts[user_id][command_name] = max(0, self.counts[user_id][command_name] - 1)
        self.save_data()

        embed = discord.Embed(
            title=f"{command_name.capitalize()} Count Decremented",
            description=f"Current count for {command_name}: {self.counts[user_id][command_name]}/{self.goals[command_name]}",
            color=discord.Color.blue()
        )
        # embed.set_footer(text="If this was a mistake, use `pass {command_name}` to increment the count. Thank you!")
        await message.channel.send(embed=embed)


    async def giveaway_reminder(self, message):
        cooldown = 300 # 5 minutes in seconds
        buffer = 7 # extra seconds to ensure the cooldown has definitely expired

        await asyncio.sleep(cooldown + buffer)

        reminder_embed = discord.Embed(
            title="Giveaway Cooldown Reminder",
            description="You can now use the command again.\n ",
            color=discord.Color.green()
        )

        await message.channel.send(
            content=message.author.mention,
            embed=reminder_embed
        )

    
    @app_commands.command(name="dank-progress")
    async def dank_progress(self, interaction: discord.Interaction):
        data = self.counts.get(str(interaction.user.id), {"giveaway": 0})

        if not data:
            await interaction.response.send_message(
                "No commands tracked yet.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"{interaction.user.name}'s progress",
            description="\n".join(
                f"**{cmd}**: {count}/{self.goals[cmd]} \n(**{(count / self.goals[cmd]) * 100:.2f}%**)" for cmd, count in data.items()
            ),
            color=discord.Color.blue()
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(DankReminderCommandsCog(bot))