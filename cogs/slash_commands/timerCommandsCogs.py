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
from utils.timer_task import TimerTask
from utils.timer_manager import TimerManager
    

class TimerCommandsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = TimerManager()


    def build_timer_embed(self, reminder, start_time, footer_text):
        '''
        Helper function to build the timer end embed with the reminder message, start time, and footer text.
        '''
        embed = discord.Embed(
            title="<a:purpletick:1148523911634497616> Timer Ended!",
            description=f"<:purple_dot:1167142077281353799> **Your reminder message:**\n{reminder}",
            color=discord.Color.green()
        )

        embed.set_footer(text=footer_text)
        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1250019842329808916.webp?size=128&animated=true")

        embed.add_field(
            name="Started at",
            value=f"<t:{int(start_time)}:f>",
            inline=False
        )
        return embed
    

    def check_duration_bounds(self, duration_seconds):
        min_time = 10 # seconds
        max_time = 24 * 3600 # 24 hours in seconds

        return min_time <= duration_seconds <= max_time


    # * Starting with a simple command for timer/reminder to understand
    @app_commands.command(name="start-timer", description="Starts a timer for a specified duration, maybe with a reminder message.")
    @app_commands.describe(duration="Duration of the timer in seconds/minutes/hours (s/m/h)", reminder="(Optional) A reminder message to be sent when the timer ends.", channel="(Optional) Whether the reminder should be sent in the channel or DM, by default it's sent to the channel.")
    async def start_timer(self, interaction: discord.Interaction, duration: app_commands.Transform[int, DurationTransformer], reminder: str = "No reminder message provided.", channel: bool = True):
        # get the user ID      
        # user_id = interaction.user.id
        
        error_messages = [
            "Make sure to have your DMs open to receive the reminder message.", 
            "You can toggle to DM reminder by choosing False for channel parameter.", 
            "If you had chosen to receive reminder in DMs instead, please check your settings to make sure DMs are enabled."
        ]
        
        fun_messages = [
            "Tons of timer but still not on time, tsk tsk!", 
            "Time flies when you're having fun, but don't forget to set your timer!", 
            "Ding dong! Time's up! Hope you had a productive time!", 
            "Timers can't fix what your mentality couldn't. Be better! Set that timer and get to work!", 
            "Time is money, but you can set a timer for free! What are you waiting for?"
        ]

        # parse the duration input
        # time_multiplier = 1
        # if duration.endswith('s'):
        #     time_multiplier = 1
        #     unit_text = "seconds"
        # elif duration.endswith('m'):
        #     time_multiplier = 60
        #     unit_text = "minutes"
        # elif duration.endswith('h'):
        #     time_multiplier = 3600
        #     unit_text = "hours"
        # else:
        #     await interaction.response.send_message("Invalid duration format. Please make sure to use the format like '10s', '5m', or '2h'.", ephemeral=True)
        #     return
        
        # try:
        #     time_value = int(duration[:-1]) * time_multiplier
            
        #     # check the bounds
        #     # if not self.check_duration_bounds(time_value):
        #     #     await interaction.response.send_message("Timer must be between 10 seconds and 24 hours!", ephemeral=True)
        #     #     return
        # except ValueError:
        #     await interaction.response.send_message("Invalid duration value. Please make sure to provide a valid number followed by 's', 'm', or 'h'.", ephemeral=True)
        #     return
        
        unit = "seconds" if duration < 60 else "minutes" if duration < 3600 else "hours"
        duration_text = f"{duration} {unit}"

        start_time = datetime.now().timestamp()
        end_time = start_time + duration
        
        # start the timer and send a confirmation message in direct message
        confirm_embed = discord.Embed(
            title=f"<a:timer:1484238304361713755>  Timer Started for {duration_text}!",
            description=f"I will remind you at <t:{int(end_time)}:t>.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=confirm_embed, view=StartTimerView(timer_task=None))

        # * jumps to the original timer response
        start_msg = await interaction.original_response()
        await asyncio.sleep(duration)

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Jump to original message",
                url=start_msg.jump_url
            )
        )
        
        # send the reminder message to the channel with a ping or DM the user based on the channel parameter
        # if channel is set to False, check if the user settings has DMs enabled, if not send the reminder to the channel with a ping and reason why the reminder is sent to the channel instead of DM
        if not channel:
            if interaction.user.dm_channel is None:
                await interaction.user.create_dm()

            try:
                embed=self.build_timer_embed(
                    reminder,
                    start_time=start_time,
                    footer_text=random.choice(fun_messages)
                )

                await interaction.user.dm_channel.send(embed=embed, view=view)

            except discord.errors.Forbidden:
                embed = self.build_timer_embed(
                    reminder,
                    start_time=start_time,
                    footer_text=random.choice(error_messages)
                )

                await interaction.response.send_message(
                    content=f"{interaction.user.mention}, I don't have permission to DM you. Please enable DMs in your settings.",
                    embed=embed,
                    view=view
                )
            
            except discord.errors.HTTPException:
                embed = self.build_timer_embed(
                    reminder,
                    start_time=start_time,
                    footer_text=random.choice(error_messages)
                )
                await interaction.response.send_message(
                    content=f"{interaction.user.mention}, I don't have permission to DM you. Please enable DMs in your settings.",
                    embed=embed,
                    view=view
                )
        else:
            # make the embed ping user with the new discord embed component
            embed = self.build_timer_embed(
                reminder,
                start_time=start_time,
                footer_text=random.choice(fun_messages)
            )

            await interaction.channel.send(
                content=f"{interaction.user.mention}",
                embed=embed,
                view=view
            )
        
        await interaction.followup.send("Timer ended.")
        
        return
        

async def setup(bot):
    await bot.add_cog(TimerCommandsCog(bot))