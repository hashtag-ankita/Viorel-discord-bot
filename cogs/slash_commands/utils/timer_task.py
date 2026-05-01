import discord
import time
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import random
from datetime import datetime, timedelta

# class CancelTimerButton(discord.ui.Button):
#     def __init__(self, timer_task):
#         super().__init__(label="<a:purplecross:1148524488875585608>", style=discord.ButtonStyle.danger)
#         self.timer_task = timer_task
    
#     async def callback(self, interaction: discord.)

class DurationTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> int:
        '''
        Transforms a duration string like '10s', '5m', '2h' into seconds.
        '''
        unit_map = {"s": 1, "m": 60, "h": 3600}

        try:
            unit = value[-1]
            amount = int(value[:-1])
            seconds = amount * unit_map.get(unit, 1)
        except (ValueError, KeyError):
            raise app_commands.AppCommandError("Invalid duration format.")
        
        if seconds < 10:
            raise app_commands.AppCommandError("Minimum duration is 10 seconds.")
        if seconds > 24 * 3600:
            raise app_commands.AppCommandError("Maximum duration is 24 hours.")
        
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
    def __init__(self, cog, user, duration, reminder, channel, start_msg_url):
        self.cog = cog
        self.user = user
        self.user_id = user.id

        self.duration = duration
        self.reminder = reminder
        self.channel = channel

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
        await asyncio.sleep(self.duration)
        await self.finish()

    async def finish(self):
        if not self.active:
            return
        
        self.active = False

        await self.send_reminder()
        self.cog.manager.remove_timer(self.user_id, self)

    async def send_reminder(self):
        users = [self.user] + list(self.joined_users)

        for u in users:
            try:
                if u.dm_channel is None:
                    await u.create_dm()

                await u.dm_channel.send(
                    f"⏰ Timer ended!\n{self.reminder}\n🔗 {self.start_msg_url}"
                )
            except:
                pass

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