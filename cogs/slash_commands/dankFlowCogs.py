import discord
from discord.ext import commands
from discord import app_commands
from datetime import *
import asyncio

'''This cog contains command related to the dank command flow, such that it shows the next command in the flow, without having the user to type it out themselves.'''

class StartFLowButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(label="Start Flow", style=discord.ButtonStyle.success)
        self.cog = cog

    
    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        self.cog.active_flows[user_id] = {
            "index": 0,
            "channel_id": interaction.channel_id,
            "message_id": None
        }

        # send first command
        await self.cog.send_next_command(interaction)

        # update UI
        await interaction.response.edit_message(
            embed=self.cog.build_status_embed(user_id),
            view=FlowControlView(self.cog, user_id=user_id)
        )

class EndFlowButton(discord.ui.Button):
    def __init__(self, cog):
        super().__init__(label="End Flow", style=discord.ButtonStyle.danger)
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if user_id in self.cog.active_flows:
            del self.cog.active_flows[user_id]
        
        await interaction.response.edit_message(
            embed=self.cog.build_status_embed(user_id),
            view=FlowControlView(self.cog, user_id=user_id)
        )

        # send an ephemeral message to confirm flow has ended
        await interaction.followup.send("Flow ended!", ephemeral=True)

class FlowControlView(discord.ui.View):
    def __init__(self, cog, user_id):
        super().__init__(timeout=None)

        self.cog = cog
        self.user_id = user_id

        if user_id in cog.active_flows:
            self.add_item(EndFlowButton(cog))
        else:
            self.add_item(StartFLowButton(cog))

class DankFlowCogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.flow_order = [
            "hunt",
            "dig",
            "beg",
            "search",
            "crime",
            "postmemes",
            "tidy"
        ]

        self.command_ids = {
            "hunt": "1011560371171102760",
            "dig": "1011560371078832204",
            "beg": "1011560371041095699",
            "tidy": "1388145631587209358",
            "search": "1011560371267579935",
            "crime": "1011560371078832202",
            "postmemes": "1011560370911072263"
        }

        self.command_delays = {
            "crime": 0,
            "postmemes": 0,
            "tidy": 0,
            "search": 0
        }

        self.active_flows = {}

    def build_status_embed(self, user_id):
        running = user_id in self.active_flows

        status = "🟢 Running" if running else "🛑 Not Running"

        command_list = ""

        for cmd in self.flow_order:
            cmd_id = self.command_ids[cmd]
            command_list += f"</{cmd}:{cmd_id}>\n"

        return discord.Embed(
            title="Dank Flow",
            description=f"Status: {status}\n\nCommands:\n{command_list}",
            color=discord.Color.green() if running else discord.Color.red()
        )


    @app_commands.command(name="startflow", description="Start the dank command flow")
    async def dankflow(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        embed = self.build_status_embed(user_id)
        view = FlowControlView(self, user_id=user_id)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    
    async def send_next_command(self, ctx, user_id=None):
        if isinstance(ctx, discord.Interaction):
            user_id = ctx.user.id
            channel = ctx.channel
        else:
            channel = ctx.channel

        flow = self.active_flows.get(user_id)
        if not flow:
            return
        
        index = flow["index"]

        cmd = self.flow_order[index]
        cmd_id = self.command_ids[cmd]

        # * to get the commands as embed
        embed = discord.Embed(
            title=f"</{cmd}:{cmd_id}>",
            color=discord.Color.green()
        )

        msg = await channel.send(embed=embed)

        # # * to get the commands as normal message
        # msg = await channel.send(f"</{cmd}:{cmd_id}>")

        flow["message_id"] = msg.id

        # loop back instead of stopping
        flow["index"] = (index + 1) % len(self.flow_order)

    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        DANK_ID = 270904126974590976

        if message.author.id != DANK_ID:
            return
        
        if not message.interaction_metadata:
            return
        
        user_id = message.interaction_metadata.user.id

        if user_id not in self.active_flows:
            return

        flow = self.active_flows.get(user_id)
        if not flow:
            return
        
        current_index = flow["index"]
        current_cmd = self.flow_order[current_index]
        
        # delete previous command message
        try:
            prev = await message.channel.fetch_message(flow["message_id"])
            await prev.delete()
        except Exception as e:
            print(f"Failed to delete previous message: {e}")

        # move forward
        flow["index"] = (current_index + 1) % len(self.flow_order)

        # delay logic
        delay = self.command_delays.get(current_cmd, 0)

        if delay > 0:
            await asyncio.sleep(delay)

        await self.send_next_command(message, user_id=user_id)

async def setup(bot):
    await bot.add_cog(DankFlowCogs(bot))
        