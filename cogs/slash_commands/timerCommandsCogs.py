'''
This cog contains commands related to timers, such as pomodoro, countdowns, and reminders.
'''
import discord
import time
from discord.ext import commands, tasks
from discord import app_commands
import os
import dotenv
import asyncio
import random
from datetime import datetime, timedelta
from .utils.timer_task import TimerTask, DurationTransformer, CancelTimerButton, StartTimerView
from .utils.timer_manager import TimerManager
    

class TimerCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = TimerManager()

    
    # * 01.05.2026 - Starting timer command (cleaner)
    @app_commands.command(name="start-timer")
    async def start_timer(self, interaction: discord.Interaction, duration: app_commands.Transform[int, DurationTransformer], reminder: str = "No reminder message provided.", channel: bool = True):
        # duration text
        if duration < 60:
            duration_text = f"{duration} seconds"
        elif duration < 3600:
            duration_text = f"{duration // 60} minutes"
        else:
            duration_text = f"{duration // 3600} hours"

        start_time = datetime.now().timestamp()
        end_time = start_time + duration

        # confirmation embed
        confirm_embed = discord.Embed(
            title=f"<a:timer:1484238304361713755>  Timer Started for {duration_text}!",
            description=f"I will remind you at <t:{int(end_time)}:t>.",
            color=discord.Color.blue()
        )

        # send initial response
        # await interaction.response.send_message(embed=confirm_embed, view=StartTimerView(timer_task=None))

        # create timer object
        timer = TimerTask(
            cog=self,
            user=interaction.user,
            duration=duration,
            reminder=reminder,
            channel=interaction.channel,
            send_in_channel=channel # store the channel preference in the timer task
        )

        await interaction.response.send_message(embed=confirm_embed, view=StartTimerView(timer_task=timer))

        start_msg = await interaction.original_response()

        timer.start_msg_url = start_msg.jump_url

        self.manager.add_timer(interaction.user.id, timer)

        # start the timer
        await timer.start()

    
    @start_timer.error
    async def start_timer_error(self, interaction: discord.Interaction, error):
        '''
        Error handler for the start_timer command. If the error is an AppCommandError, it sends the error message as a response.
        '''    
        if isinstance(error, app_commands.AppCommandError):
            await interaction.response.send_message(
                str(error),
                ephemeral=True
            )
        

async def setup(bot):
    await bot.add_cog(TimerCommandsCog(bot))