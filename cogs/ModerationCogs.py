import discord
from discord.ext import commands
from discord import app_commands

class modCommandsCogs(commands.Cog):
    '''Contains moderation commands for the bot (can be run by moderators only)'''
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="change_nickname", description="Change the nickname of a user")
    @commands.has_permissions(manage_nicknames=True)
    async def change_nickname(self, interaction: discord.Interaction, user: discord.Member, nickname: str):
        try:
            await user.edit(nick=nickname)
            await interaction.response.send_message(f"Changed **{user.display_name}**'s nickname to **{nickname}** successfully!")
        except Exception as e:
            await interaction.response.send_message(f"Sorry, an error occured: `{e}`")


    @app_commands.command(name="ban", description="ban a user")
    @commands.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        try:
            await user.ban(reason=reason)
            await interaction.response.send_message(f"User **{user.display_name}** is banned successfully!")
        except Exception as e:
            await interaction.response.send_message(f"Sorry, an error occured: ```{e}```\n**Please try again or contact the server administrators.**")

    @app_commands.command(name="unban", description="unban a user")
    @commands.has_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user: discord.User, reason: str = None):
        try:
            guild = interaction.guild
            await guild.unban(user, reason=reason)
            await interaction.response.send_message(f"User **{user.display_name}** is unbanned successfully! They may join the server again.")
        except Exception as e:
            await interaction.response.send_message(f"Sorry, an error occured: ```{e}```\n**Please try again or contact the server administrators.**")

    @app_commands.command(name="kick", description="kick a user")
    @commands.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        try:
            await user.kick(reason=reason)
            await interaction.response.send_message(f"User **{user.display_name}** is kicked successfully!")
        except Exception as e:
            await interaction.response.send_message(f"Sorry, an error occured: ```{e}```\n**Please try again or contact the server administrators.**")
            

    @app_commands.command(name="purge", description="Purge messages")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, interaction: discord.Interaction, amount: int = 5):
        if role := discord.utils.get(interaction.guild.roles, name="Moderators"):
            if role not in interaction.user.roles:
                await interaction.response.send_message("You do not have the required permissions to run this command!")
                return
        await interaction.response.defer()
        try:
            await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"**{amount}** messages are deleted successfully!")
            
        except Exception as e:
            await interaction.followup.send(f"Sorry, an error occurred: ```{e}```\n**Please try again or contact the server administrators.**")


    @app_commands.command(name="slowmode", description="set slowmode")
    @commands.has_permissions(manage_messages=True)
    async def slowmode(self, interaction: discord.Interaction, amount: int = 10):
        try:
            await interaction.channel.edit(slowmode_delay=amount)
            await interaction.response.send_message(f"Set slowmode to **{amount}** seconds in this channel!")
        except Exception as e:
            await interaction.response.send_message(f"Sorry, an error occured: ```{e}```\n**Please try again or contact the server administrators.**")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(modCommandsCogs(client))