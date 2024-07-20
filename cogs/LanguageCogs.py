import discord
from discord.ext import commands
from discord import app_commands
from requests import *
from googletrans import Translator
from json import *
from asyncio import *
import discord.ui
import discord.ext.commands

'''some snippets used from: https://github.com/yllberisha/Translating_Discord_Bot/blob/main/ppi_bot.py'''
# Create a dictionary of flag emojis and their corresponding language codes
languages = {
"🇺🇸": "en",
"🇩🇪": "de",
"🇫🇷": "fr",
"🇪🇸": "es",
"🇮🇹": "it",
"🇵🇹": "pt",
"🇷🇺": "ru",
"🇦🇱": "sq",
"🇸🇦": "ar",
"🇧🇦": "bs",
"🇧🇬": "bg",
"🇨🇳": "zh-CN",
"🇭🇷": "hr",
"🇨🇿": "cs",
"🇩🇰": "da",
"🇪🇪": "et",
"🇫🇮": "fi",
"🇬🇷": "el",
"🇭🇺": "hu",
"🇮🇩": "id",
"🇮🇳": "hi",
"🇮🇪": "ga",
"🇮🇸": "is",
"🇮🇱": "he",
"🇯🇵": "ja",
"🇰🇷": "ko",
"🇱🇻": "lv",
"🇱🇹": "lt",
"🇲🇹": "mt",
"🇲🇪": "sr",
"🇳🇱": "nl",
"🇳🇴": "no",
"🇵🇰": "ur",
"🇵🇱": "pl",
"🇵🇹": "pt",
"🇷🇴": "ro",
"🇷🇸": "sr",
"🇸🇦": "ar",
"🇸🇰": "sk",
"🇸🇮": "sl",
"🇸🇬": "sv",
"🇹🇭": "th",
"🇹🇷": "tr",
"🇹🇼": "zh-TW",
"🇺🇦": "uk",
"🇻🇦": "la"
}

class langCommandsCogs(commands.Cog):
    '''Contains language related commands for the bot'''
    def __init__(self, client: commands.Bot):
        self.client = client

    @app_commands.command(name="define", description="finds meaning of any given word")
    async def define(self, interaction: discord.Interaction, word: str):
        try:
            response = get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
            data = response.json()

            if isinstance(data, dict) and data.get("title") == "No Definitions Found":
                await interaction.response.send_message(f"Sorry, the definition for the word **{word}** could not be found.")
                return

            definitions = data[0]['meanings'][0]['definitions'][0]['definition']
            # example = data[0]['meanings'][0]['definitions'][0].get('example', 'No example available')
            phonetics = data[0]['phonetics'][0].get('text', 'No phonetics available')

            embed = discord.Embed(title=f"Definition of {word}", color=discord.Color.blue())
            embed.add_field(name="Definition", value=definitions, inline=False)
            # embed.add_field(name="Example", value=example, inline=False)
            embed.add_field(name="Phonetics", value=phonetics, inline=False)

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"```Error occured: {str(e)}```")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.emoji:
            reacted_emoji_name = str(reaction.emoji)  # Get emoji as string
            # lang_code = reacted_emoji_name[-2:]  # Extract last two characters (language code)
            # print(f"Reacted emoji: {reacted_emoji_name}, Extracted lang code: {lang_code}")
            
            if reacted_emoji_name in languages:
                selected_lang = languages[reacted_emoji_name]
                # print(f"Selected language: {selected_lang}")
                sent_message = str(reaction.message.content)
                translator = Translator()

                try:
                    # Detect the language of the original message
                    detected_lang = translator.detect(sent_message)
                    if detected_lang is None:
                        await reaction.message.channel.send("Could not detect the language of the message.")
                        return
                    
                    # print(f"Detected language: {detected_lang.lang}, Confidence: {detected_lang.confidence}")

                    # Translate the message
                    translation = translator.translate(sent_message, dest=selected_lang)
                    if translation is None or translation.text is None:
                        await reaction.message.channel.send("Translation failed.")
                        return
                    
                    translated_message = translation.text
                    # print(f"Translated message: {translated_message}")

                    translationEmbed = discord.Embed(title="Translation", color=discord.Color.blurple())
                    translationEmbed.add_field(name="Detected Language", value=detected_lang.lang, inline=False)
                    translationEmbed.add_field(name="Original Message", value=sent_message, inline=False)
                    translationEmbed.add_field(name="Selected Language", value=selected_lang, inline=False)
                    translationEmbed.add_field(name="Translated Message", value=translated_message, inline=False)
                    await reaction.message.channel.send(embed=translationEmbed)
                except Exception as e:
                    # print(f"Exception occurred: {str(e)}")
                    await reaction.message.channel.send(f"Translation error: {str(e)}")
            else:
                await reaction.message.channel.send(f"Invalid emoji: {reacted_emoji_name}")

    @app_commands.command(name="translate", description="translate text from one language to another")
    async def translate(self, interaction: discord.Interaction, text: str):
        pass


    @app_commands.command(name="add_writing_goal", description="add your writing goals (in words)")
    async def add_writing_goal(self, interaction: discord.Interaction, goal: int):
        user_id = str(interaction.user.id)

        with open("global_writer_profiles.json") as f:
            data = load(f)

        if user_id in data and data[user_id]['goal']:
            existing_goal = data[user_id]
            await interaction.response.send_message(f"You already have a writing goal of {existing_goal['goal']} words. Do you want to update it to {goal} words? (yes/no)")

            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                response = await self.client.wait_for("message", check=check, timeout=30.0)

                if response.content.lower() in ["yes", "y"]:
                    existing_goal["goal"] = goal
                    await interaction.followup.send(f"Updated your writing goal to {goal} words. Good luck!")
                elif response.content.lower() in ["no", "n", None]:
                    await interaction.followup.send(f"Change cancelled. Your writing goal of {existing_goal['goal']} words stays unchanged.")
                else:
                    await interaction.followup.send("Invalid input. Please type 'yes' or 'no'.")

            except TimeoutError:
                await interaction.followup.send(f"You didn't respond in time. So the change is cancelled. Your writing goal of {existing_goal['goal']} words stays unchanged.")
        elif user_id in data and not data[user_id]['goal']:
            data[user_id]['goal'] = goal
            data[user_id]['current_progress'] = 0
            data[user_id]['progress_rate'] = None

            await interaction.response.send_message(f"Added your new writing goal of {goal} words. Good luck!")
        else:
            # Add new writing goal for the user
            data[user_id] = {
                "username" : interaction.user.name,
                "goal": goal,
                "current_progress": 0,
                "progress_rate": None,
                "level": 0
            }

            await interaction.response.send_message(f"Added your writing goal of {goal} words. Good luck!")

        with open("global_writer_profiles.json", "w") as f:
            dump(data, f, indent=2)

    # @app_commands.command(name="check_writing_goal", description="check your writing goals")
    # async def check_writing_goal(self, interaction: discord.Interaction):
    #     user_id = str(interaction.user.id)

    #     with open("global_writer_profiles.json") as f:
    #         data = load(f)

    #     if user_id in data:
    #         user = data[user_id]
    #         await interaction.response.send_message(f"Your writing goal is **{user['goal']}** words.")
    #     else:
    #         await interaction.response.send_message("You haven't set a writing goal yet.")


    @app_commands.command(name="check_writing_progress", description="check your writing progress")
    async def check_writing_progress(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        with open("global_writer_profiles.json") as f:
            data = load(f)

        if user_id in data:
            user = data[user_id]

            progress_embed = discord.Embed(
                title=f"Writing Progress - **{user['username']}**",
                description=f"**__Current writing goal:__** *{str(user['goal']) + str(' word' if user['goal'] == 1 else ' words') if user['goal'] else 'No goal set'}*",
            )

            progress_embed.add_field(name="**__Writing Progress__**", value=f"{user['current_progress']}", inline=True)
            progress_embed.add_field(name="**__Progress Rate__**", value=f"{user['progress_rate']}", inline=True)
            progress_embed.add_field(name="**__Level__**", value=f"You are at level {user['level']}.", inline=False)
            progress_embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=progress_embed)
        else:
            await interaction.response.send_message("You haven't set a writing goal yet.")

        
    #UPDATED WRITER PROFILE COMMAND (replacing /check_writing_progress)
    @app_commands.command(name="my_writer_profile", description="check your writer profile")
    async def my_writer_profile(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        with open("global_writer_profiles.json") as f:
            data = load(f)
        
        if user_id in data:
            user = data[user_id]

            profile_embed = discord.Embed(
            title=f"{user['username']}'s writing profile",
            description=f"{user['bio']}" if user['bio'] else "No bio set. (*Reach level 5 with a total word count of 1k to unlock bio*)" + f"\n\n**Current writing goal:** {str(user['goal']) + str(' word' if user['goal'] == 1 else ' words') if user['goal'] else 'No goal set'}",
            color=discord.Color.blue()
        )

            profile_embed.set_thumbnail(url=interaction.user.display_avatar.url)
            profile_embed.add_field(name="**Writing Progress:**", value=f"{user['current_progress']}", inline=True)
            profile_embed.add_field(name="**Progress Rate:**", value=f"{user['progress_rate']}", inline=True)
            profile_embed.add_field(name="**Total Word Count:**", value=f"You have written {user['total_word_count']} words so far." if user['total_word_count'] else "You haven't written anything yet.", inline=False)
            profile_embed.add_field(name="**Level:**", value=f"You are at level {user['level']}.", inline=False)

            if user['banner']:
                profile_embed.set_image(url=user['banner'])
            else:
                profile_embed.add_field(name="**Banner:**", value="No banner set.", inline=False)

            profile_embed.set_footer(text="Any mistake in the stats? Let us know about it with /complain command.")

            #the buttons with the embed
            view = discord.ui.View()

            async def check_interaction(self, interaction: discord.Interaction) -> bool:
                if interaction.user.id != self.user.id:
                    await interaction.response.send_message("You can't interact with this button!", ephemeral=True)
                    return False
                return True

            async def set_goal_callback(interaction: discord.Interaction):
                if not await self.view.check_interaction(self, interaction):
                    return
                if user['goal']:
                    existing_goal = user['goal']
                    await interaction.response.send_message(f"You already have an existing goal. Try deleting it to set a new one.", ephemeral=True)
                else:
                    modal = discord.ui.Modal(
                        title="Set a Writing Goal",
                        custom_id="set_goal",
                        timeout=60
                    )
                    goal_input = discord.ui.TextInput(placeholder="Enter your new writing goal.", label="Writing Goal", custom_id="goal", style=discord.TextStyle.short)
                    modal.add_item(goal_input)
                    await interaction.response.send_modal(modal)


            async def update_progress_callback(interaction: discord.Interaction):
                if user['goal']:
                    await interaction.response.send_message("Please set a goal first.", ephemeral=True)
                else:
                    modal = discord.ui.Modal(
                        title="Updating writing progress",
                        custom_id="update_progress",
                        timeout=60
                    )

                    update_input = discord.ui.TextInput(placeholder="Enter your new writing progress.", label="Writing Progress (word count)", custom_id="progress", style=discord.TextStyle.short)
                    modal.add_item(update_input)
                    await interaction.response.send_modal(modal)

            async def delete_goal_callback(interaction: discord.Interaction):
                pass

            async def cancel_callback(interaction: discord.Interaction):
                await interaction.response.send_message("Action cancelled.", ephemeral=False)
                view.stop()

            async def refresh_callback(interaction: discord.Interaction):
                pass

            async def bio_callback(interaction: discord.Interaction):
                if user['level'] != 5 or user['total_word_count'] < 1000:
                    await interaction.response.send_message("You need to reach level 5 with a total word count of 1k to unlock this feature.", ephemeral=True)
                else:
                    pass
                    

            async def banner_callback(interaction: discord.Interaction):
                if user['level'] != 10 or user['total_word_count'] < 2500:
                    await interaction.response.send_message("You need to reach level 10 with a total word count of 2.5k to unlock this feature.", ephemeral=True)
                else:
                    pass

            #set goal button
            set_goal_button = discord.ui.Button(label="Set Goal", style=discord.ButtonStyle.green, custom_id="set_goal")
            delete_goal_button = discord.ui.Button(label="Delete Goal", style=discord.ButtonStyle.red, custom_id="delete_goal")
            bio_button = discord.ui.Button(label="Edit Bio", style=discord.ButtonStyle.blurple, custom_id="bio", emoji="📝", row=1)
            banner_button = discord.ui.Button(label="Edit Banner", style=discord.ButtonStyle.blurple, custom_id="banner", emoji="🖼", row=1)
            update_progress_button = discord.ui.Button(label="Update Progress", style=discord.ButtonStyle.primary, custom_id="update_progress")

            if user['goal']:
                set_goal_button.disabled = True
            else:
                delete_goal_button.disabled = True
                update_progress_button.disabled = True 

            if not user['bio']:
                bio_button.label = "Add Bio"
            
            if not user['banner']:
                banner_button.label = "Add Banner"

            cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, custom_id="cancel", emoji="❌", row=1)

            refresh_button = discord.ui.Button(style=discord.ButtonStyle.gray, custom_id="refresh", emoji="🔄", row=1)

            set_goal_button.callback = set_goal_callback
            update_progress_button.callback = update_progress_callback
            delete_goal_button.callback = delete_goal_callback
            cancel_button.callback = cancel_callback
            
            view.add_item(set_goal_button)
            view.add_item(update_progress_button)
            view.add_item(delete_goal_button)
            view.add_item(bio_button)
            view.add_item(banner_button)
            view.add_item(cancel_button)
            view.add_item(refresh_button)

            await interaction.response.send_message(embed=profile_embed, view=view)
            if not user['banner'] and user['level'] == 10 and user['total_word_count'] >= 2500:
                await interaction.followup.send("You haven't set a banner yet.", ephemeral=True)
            if not user['bio'] and user['level'] == 5 and user['total_word_count'] >= 1000:
                await interaction.followup.send("You haven't set a bio yet.", ephemeral=True)
        else:
            await interaction.response.send_message("You do not have a profile set up yet!")


    @app_commands.command(name="update_writing_progress", description="update your writing progress")
    async def update_writing_progress(self, interaction: discord.Interaction, progress: int):
        user_id = str(interaction.user.id)
            
        with open("global_writer_profiles.json") as f:
            data = load(f)

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        if user_id in data:
            user = data[user_id]
            if user['goal']:                
                confirmation_embed = discord.Embed(
                    title="Update your writing progress",
                    description=f"Would you like to **__update your writing word count__** to {progress} words or **__add it to the last updated word count__**?",
                    color=discord.Color.blue()
                )

                view = discord.ui.View()

                #define update callback
                async def update_callback(interaction: discord.Interaction):
                    user['total_word_count'] = (user['total_word_count'] - user['current_progress']) + progress 
                    user['current_progress'] = progress
                    user['progress_rate'] = f"{round((user['current_progress']/user['goal']) * 100, 2)}%"
                    await interaction.response.send_message(f"Your word count has been updated to {progress} words.", ephemeral=True)
                    await self.update_data(interaction, user, data)
                    view.stop()

                #define add callback
                async def add_callback(interaction: discord.Interaction):
                    user['current_progress'] += progress
                    user['progress_rate'] = f"{round((user['current_progress']/user['goal']) * 100, 2)}%"
                    user['total_word_count'] += progress
                    await interaction.response.send_message(f"{progress} words have been added to your current word count.", ephemeral=True)
                    await self.update_data(interaction, user, data)
                    view.stop()

                #define cancel callback
                async def cancel_callback(interaction: discord.Interaction):
                    #the buttons turn grey, inactive
                    cancel_button.disabled = True
                    update_button.disabled = True
                    add_button.disabled = True
                    await interaction.response.send_message("Operation cancelled.", ephemeral=False)
                    view.stop()

                #a button to select to update or add
                update_button = discord.ui.Button(label="Update", style=discord.ButtonStyle.primary, custom_id="update", emoji="✏️")
                add_button = discord.ui.Button(label="Add", style=discord.ButtonStyle.primary, custom_id="add", emoji="➕")
                cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.danger, custom_id="cancel", emoji="❌")

                update_button.callback = update_callback
                add_button.callback = add_callback
                cancel_button.callback = cancel_callback

                view.add_item(update_button)
                view.add_item(add_button)
                view.add_item(cancel_button)

                #wait for button press
                await interaction.response.send_message(embed=confirmation_embed, view=view)

        else:
            await interaction.response.send_message("You have not set a goal yet. Use `/set_writing_goal` to set a goal.", ephemeral=False)

    async def update_data(self, interaction: discord.Interaction, user: dict, data: dict):
        try:
            if user['current_progress'] >= user['goal']:
                user['level'] += 1
                user['current_progress'] = user['current_progress'] - user['goal']
                if user['current_progress']:
                    user['progress_rate'] = f"{round((user['current_progress']/user['goal']) * 100, 2)}%"
                else:
                    user['progress_rate'] = None
                
                await interaction.followup.send(f"Congratulations! You have reached your writing goal. You are now at level {user['level']}.")
            else:
                user['progress_rate'] = f"{round((user['current_progress']/user['goal']) * 100, 2)}%"
                await interaction.followup.send(f"Your writing progress has been updated to {user['current_progress']} words.")

            with open("global_writer_profiles.json", "w") as f:
                dump(data, f, indent=2)

        except Exception as e:
            await interaction.followup.send(f"Sorry, an error occurred: ```{e}```\n**Please try again or contact the server administrators.**")


    @app_commands.command(name="delete_writing_goal", description="delete your writing goal")
    async def delete_writing_goal(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)

        with open("global_writer_profiles.json") as f:
            data = load(f)

        if user_id in data and data[user_id]['goal']:
            user = data[user_id]

            user['goal'] = None
            user['current_progress'] = None
            user['progress_rate'] = None
            await interaction.response.send_message("Your writing goal has been deleted.")
        else:
            await interaction.response.send_message("You haven't set a writing goal yet.")

        with open("global_writer_profiles.json", "w") as f:
            dump(data, f, indent=2)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(langCommandsCogs(client))