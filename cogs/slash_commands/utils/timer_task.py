import discord
import time
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import random
from datetime import datetime, timedelta

class DurationTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> int:
        '''
        Transforms a duration string like '10s', '5m', '2h' into seconds.
        '''
        unit_map = {"s": 1, "m": 60, "h": 3600}

        try:
            unit = value[-1]
            amount = int(value[:-1])
            seconds = amount * unit_map[unit]
        except (ValueError, KeyError, IndexError):
            raise app_commands.AppCommandError(
                "Invalid duration format. Use formats like '10s', '5m', or '2h'."
            )
        
        # * Bounds check        
        if seconds < 10:
            raise app_commands.AppCommandError(
                "Timer must be at least 10 seconds."
            )
            
        if seconds > 24 * 3600:
            raise app_commands.AppCommandError(
                "Timer cannot be longer than 24 hours."
            )
        
        return seconds


class CancelTimerButton(discord.ui.Button):
    def __init__(self, timer_task):
        super().__init__(
            # label="",
            style=discord.ButtonStyle.secondary,
            emoji="<:purple_cross:1148524488875585608>"
        )
        self.timer_task = timer_task

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.timer_task.user:
            await interaction.response.send_message("This is not your timer.", ephemeral=True)
            return

        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
            await interaction.response.send_message("Timer cancelled successfully.", ephemeral=True)

        else:
            await interaction.response.send_message("Timer has already ended or was not found.", ephemeral=True)


class RemindMeTooButton(discord.ui.Button):
    def __init__(self, timer_task):
        super().__init__(
            label="Remind me too",
            style=discord.ButtonStyle.secondary,
            
        )
        self.timer_task = timer_task

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self.timer_task.user:
            await interaction.response.send_message("You are already the one who set this timer.", ephemeral=True)
            return
        
        if self.timer_task and not self.timer_task.done():
            # logic to add the user to the reminder list and send them a DM when the timer ends
            self.timer_task.add_reminder_user(interaction.user)
            await interaction.response.send_message("You will be reminded when the timer ends.", ephemeral=True)
        else:
            await interaction.response.send_message("Timer has already ended or was not found.", ephemeral=True)


class StartTimerView(discord.ui.View):
    def __init__(self, timer_task):
        super().__init__(timeout=None)
        self.timer_task = timer_task
        self.add_item(CancelTimerButton(timer_task))
        self.add_item(RemindMeTooButton(timer_task))
    
    async def on_timeout(self):
        '''
        When the view times out, we can perform any necessary cleanup here.
        '''
        if self.timer_task and not self.timer_task.done():
            self.timer_task.cancel()
            await self.timer_task.channel.send("Timer cancelled due to timeout.")
        else:
            await self.timer_task.channel.send("Timer has already ended or was not found.")

        self.stop()  # Stop the view to prevent further interactions after timeout


class TimerTask:
    def __init__(self, cog, user, duration, reminder, channel, start_msg_url, send_in_channel=True):
        self.cog = cog
        self.user = user
        self.user_id = user.id

        self.duration = duration
        self.reminder = reminder
        self.channel = channel
        self.send_in_channel = send_in_channel

        self.start_time = int(time.time())
        self.end_time = self.start_time + duration

        self.start_msg_url = start_msg_url

        self.joined_users = set()
        self.active = True
        self.task = None # asyncio task

    # * STATE CHECKS
    def is_active(self):
        return self.active
    
    def is_finished(self):
        return not self.active
    
    def can_join(self):
        return self.active
    
    def can_cancel(self, user_id):
        return user_id == self.user_id and self.active

    async def start(self):
        self.task = asyncio.create_task(self._run())
    
    async def _run(self):
        try:
            print(f"[TIMER] Started for {self.duration}s") # ! to debug

            await asyncio.sleep(self.duration)

            print("[TIMER] Woke up, finishing...") # ! to debug

            await self.finish()

        except Exception as e:
            print(f"[TIMER ERROR] {e}")
        # await asyncio.sleep(self.duration)
        # await self.finish()

    async def finish(self):
        if not self.active:
            # ! to debug
            print(f"Timer for user {self.user_id} already inactive. Skipping reminder.")
            return
        
        # ! to debug
        print(f"Timer for user {self.user_id} finished. Sending reminder.")
        self.active = False

        await self.send_reminder()
        # ! to debug
        print(f"Reminder sent for user {self.user_id}. Cleaning up timer.")
        self.cog.manager.remove_timer(self.user_id, self)

    
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

    async def send_reminder(self):
        # users = [self.user] + list(self.joined_users)

        fun_messages = [
            "Tons of timer but still not on time, tsk tsk!", 
            "Time flies when you're having fun, but don't forget to set your timer!", 
            "Ding dong! Time's up! Hope you had a productive time!", 
            "Timers can't fix what your mentality couldn't. Be better! Set that timer and get to work!", 
            "Time is money, but you can set a timer for free! What are you waiting for?"
        ]

        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="Jump to Timer Start",
                url=self.start_msg_url
            )
        )

        embed = self.build_timer_embed(
            reminder=self.reminder,
            start_time=self.start_time,
            footer_text=random.choice(fun_messages)
        )

        # for u in users:
        if self.send_in_channel:
            await self.channel.send(
                content=self.user.mention,
                embed=embed,
                view=view
            )
        else:
            try:
                if self.user.dm_channel is None:
                    await self.user.create_dm()

                await self.user.dm_channel.send(
                    embed=embed,
                    view=view
                )

            except:
                # fallback to channel
                await self.channel.send(
                    content=f"{self.user.mention} (Couldn't DM you)",
                    embed=embed,
                    view=view
                )

    # ! TODO: check chatgpt for rest of the code and change parts of it as per the need - 20.03.2026

    # * Continuing the code: 01.05.2026
    async def cancel(self, user):
        if not self.can_cancel(user.id):
            return False, "You are not part of this timer."
        
        self.active = False

        if self.task:
            self.task.cancel()

        return True, "Timer cancelled."
    
    def join(self, user):
        if not self.can_join():
            return False, "Timer already ended."
        
        if user == self.user:
            return False, "You are already part of the timer."
        
        self.joined_users.add(user)
        return True, "You will be reminded when the timer ends."